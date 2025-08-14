KRMU Lost & Found System
A full-stack web application designed to help students and staff at K.R. Mangalam University report, find, and manage lost or found items on campus. The platform provides a simple, intuitive interface for all users and a secure, password-protected admin panel for managing the item listings.

✨ Features
Public User Interface: Anyone can visit the site to view the list of lost and found items.

Report Items: Easy-to-use pop-up forms for reporting a lost item or a found item.

Dynamic Filtering: Users can filter items by status (lost/found), category (electronics, books, etc.), and whether the item has been resolved.

Statistics Dashboard: An at-a-glance view of the total number of lost, found, and resolved items.

Secure Admin Panel: A separate, password-protected area for administrators to manage the system.

Admin Capabilities: Admins can edit item details, delete incorrect or spam listings, and mark items as "Resolved" once they have been returned to their owner.

🛠️ Technology Stack
Backend: Python with the Flask framework.

Database: Flask-SQLAlchemy for object-relational mapping. Deployed with PostgreSQL.

Frontend: Standard HTML5, CSS3, and JavaScript.

API Communication: The frontend communicates with the backend via a RESTful API, with Cross-Origin Resource Sharing (CORS) handled by Flask-Cors.

Deployment: Hosted on Render with Gunicorn as the production WSGI server.

🚀 Live Application
You can access the live, deployed version of the application here:

https://krmu-lost-found.onrender.com

🔧 How to Use
Public View
The homepage displays all active lost and found items.

Use the filters at the top of the page to narrow down your search.

Click "Report Lost Item" or "Report Found Item" to open a form and submit the details of an item.

Admin Access
Click the "Admin" link in the navigation bar.

You will be prompted to log in. Use the following default credentials:

Username: admin

Password: *********

Once logged in, you will see the admin dashboard, where you have the power to:

Edit: Change the details of any item.

Mark Resolved/Unresolve: Change an item's status.

Delete: Permanently remove an item listing from the database.
