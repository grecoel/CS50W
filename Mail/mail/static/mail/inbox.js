document.addEventListener('DOMContentLoaded', function () {
  // Load inbox by default if the element exists
  if (document.querySelector('#emails-view')) {
    load_mailbox('inbox');
  }

  // Event listeners for navbar buttons
  document.querySelector('#inbox')?.addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent')?.addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived')?.addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose')?.addEventListener('click', () => compose_email('New Email'));

  // Handle compose email form submission
  document.querySelector('#compose-form')?.addEventListener('submit', function (event) {
    event.preventDefault();

    // Gather form data
    const recipients = document.querySelector('#compose-recipients').value.trim();
    const subject = document.querySelector('#compose-subject').value.trim();
    const body = document.querySelector('#compose-body').value.trim();

    // Send email via API
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({ recipients, subject, body })
    })
      .then(response => response.json())
      .then(result => {
        if (result.error) {
          alert(`Error: ${result.error}`);
        } else {
          load_mailbox('sent');
        }
      })
      .catch(error => console.error('Error:', error));
  });

  // Delegated event handling for email actions
  document.body.addEventListener('click', event => {
    const target = event.target;
    const emailId = target.dataset.email;

    if (!emailId) return;

    // View email
    if (target.classList.contains('view')) {
      view_email(emailId);
    }

    // Archive/unarchive email
    if (target.classList.contains('archive')) {
      archive_email(emailId);
    }
  });
});

// Display compose email view
function compose_email(state, email = null) {
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Reset form fields
  document.querySelector('#compose-recipients').value = email?.sender || '';
  document.querySelector('#compose-subject').value = email ? `Re: ${email.subject}` : '';
  document.querySelector('#compose-body').value = email
    ? `On ${email.timestamp}, ${email.sender} wrote:\n${email.body}\n\n`
    : '';
}

// Load specified mailbox
function load_mailbox(mailbox) {
  const emailsView = document.querySelector('#emails-view');
  const composeView = document.querySelector('#compose-view');
  const emailView = document.querySelector('#email-view');

  // Show the emails view and hide others
  if (emailsView) {
    emailsView.style.display = 'block';
    composeView.style.display = 'none';
    emailView.style.display = 'none';

    // Update mailbox title
    emailsView.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    // Fetch and display emails
    fetch(`/emails/${mailbox}`)
      .then(response => response.json())
      .then(emails => {
        if (emails.length === 0) {
          emailsView.innerHTML += '<div>No emails to display...</div>';
          return;
        }

        emails.forEach(email => {
          const emailDiv = document.createElement('div');
          emailDiv.className = `email ${email.read ? 'read' : 'unread'}`;
          emailDiv.innerHTML = `
            <span><b>${email.sender}</b></span>
            <span>${email.subject}</span>
            <span class="timestamp">${email.timestamp}</span>
          `;

          // Add view button
          const viewButton = document.createElement('button');
          viewButton.className = 'btn btn-sm btn-primary view float-right';
          viewButton.dataset.email = email.id;
          viewButton.innerText = 'View';
          emailDiv.appendChild(viewButton);

          // Add archive button if applicable
          if (mailbox !== 'sent') {
            const archiveButton = document.createElement('button');
            archiveButton.className = 'btn btn-sm btn-secondary archive float-right';
            archiveButton.dataset.email = email.id;
            archiveButton.innerText = email.archived ? 'Unarchive' : 'Archive';
            emailDiv.appendChild(archiveButton);
          }

          emailsView.appendChild(emailDiv);
        });
      })
      .catch(error => console.error('Error fetching emails:', error));
  }
}

// View a specific email
function view_email(emailId) {
  fetch(`/emails/${emailId}`)
    .then(response => response.json())
    .then(email => {
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'none';
      document.querySelector('#email-view').style.display = 'block';

      document.getElementById('from').innerText = email.sender;
      document.getElementById('to').innerText = email.recipients.join(', ');
      document.getElementById('subject').innerText = email.subject;
      document.getElementById('date').innerText = email.timestamp;
      document.getElementById('emailBody').innerText = email.body;

      // Add reply button functionality
      const replyButton = document.getElementById('replyButton');
      replyButton.onclick = () => compose_email('Reply', email);
    })
    .catch(error => console.error('Error viewing email:', error));

  // Mark the email as read
  fetch(`/emails/${emailId}`, {
    method: 'PUT',
    body: JSON.stringify({ read: true })
  });
}

// Archive or unarchive email
function archive_email(emailId) {
  fetch(`/emails/${emailId}`)
    .then(response => response.json())
    .then(email => {
      fetch(`/emails/${emailId}`, {
        method: 'PUT',
        body: JSON.stringify({ archived: !email.archived })
      })
        .then(() => load_mailbox('inbox'))
        .catch(error => console.error('Error archiving email:', error));
    });
}
