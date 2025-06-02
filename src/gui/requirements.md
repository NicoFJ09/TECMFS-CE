## ✅ **🌐 Main Features & UI Task List**

### 📌 **1. GUI Layout Foundation**

* [X] Create main window layout with top bar, disk panel, file table, and log panel
* [X] Use layout manager to support dynamic resizing and clean separation (e.g. `QSplitter` or grid layout)

---

### 💽 **2. Disk Visualization Panel**

* [X] Create a visual representation for each disk (as blocks or labeled panels)
* [X] Assign color/status (OK, Failed, Busy) using color coding
* [X] Implement disk **selection logic** (click-to-select, only one active at a time)

---

### 🔼 **3. Top Action Bar (Per Disk Actions)**

* [X] Add **Upload File** button – opens file dialog for selected disk
* [X] Add **Reboot Disk** button – sends reboot request for selected disk

---

### 📁 **4. File Management Table**

* [X] Add **search bar** to filter file list (live search by filename)
* [X] Create **file table** with columns: File Name, Size, Actions
* [X] Show only files for the selected disk
* [X] Add **Delete** button per row (deletes file from selected disk)
* [X] Add **Download** button per row (downloads file from selected disk)

---

### 🔗 **5. Client-Server Communication**

* [ ] Build client module to fetch disk status (auto-refresh every X seconds)
* [ ] Fetch file list for selected disk
* [ ] Implement upload functionality with progress/status
* [ ] Implement delete and download endpoints
* [ ] Implement reboot disk request (triggered by button)

---

### 📜 **6. Log Panel**

* [ ] Create scrolling log panel at bottom of UI
* [ ] Display timestamped messages for: uploads, deletions, errors, reboots
* [ ] Append logs on all client-server exchanges
* [ ] (Optional) Add “Clear Log” button

---

### 🧪 **7. State Handling & Feedback**

* [ ] Implement disk status refresh timer (e.g. every 3–5 seconds)
* [ ] Disable actions during pending operations (e.g., while uploading)
* [ ] Highlight failed or busy disks (gray out buttons or show warning)
* [ ] Display error messages in log panel for failed requests

---

### 🧰 **8. Code Structure & Clean-up**

* [ ] Organize code into modules: GUI, API client, logging, config
* [ ] Use signals/slots or callbacks to keep UI responsive
* [ ] Comment and document key methods (upload, reboot, etc.)

---

### 📦 **9. Packaging & Testing**

* [ ] Add test functions for each client action (mock server)
* [ ] Create requirements.txt or setup.py for installation
* [ ] Write minimal usage documentation (GUI usage, how to run)

---

## 🧭 Optional Stretch Goals

* [ ] Implement drag-and-drop for file uploads
* [ ] Add context menu (right-click) for file actions
* [ ] Add disk usage bar (progress bar below each disk)