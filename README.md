
# ✍️ BanglaOCR: A Platform to Collect Bangla Handwriting for OCR Models

**Bangla OCR Handwriting Data** is a full-stack web application designed to **crowdsource handwritten Bangla text** for building large-scale OCR datasets. It provides a clean submission portal for users and a robust backend for data moderation, tracking, and export.

---

## 🌐 Live Demo 

https://bangla-ocr-data-web.vercel.app/ (frontend)
https://hossainimamrony71.pythonanywhere.com/ (API Endpoint)

---



## 🧠 Key Features

* Weighted random Bangla prompt selection
* Direct, secure client-side uploads to **Cloudinary**
* Real-time status updates during submission
* RESTful API using **Django + DRF**
* Admin-only moderation dashboard (via API for now)
* Verified submission export as `.zip` with `CSV` labels
* Decoupled architecture: Vanilla JS frontend + DRF backend

---

## 🔧 Backend: Django REST Framework

The backend powers secure APIs for serving prompts, logging submissions, moderating content, and exporting verified data.

### 📦 API Endpoints

#### `GET /api/prompt/`

* **Purpose:** Serve a Bangla text prompt using weighted random logic (prompts with fewer submissions appear more)
* **Permissions:** Public
* **Response:**

```json
{
  "id": 1,
  "text": "বাংলা আমার মাতৃভাষা।"
}
```

---

#### `GET /api/cloudinary-config/`

* **Purpose:** Provide a secure signature for client-side Cloudinary uploads
* **Permissions:** Public
* **Response:**

```json
{
  "api_key": "...",
  "cloud_name": "...",
  "timestamp": "...",
  "signature": "..."
}
```

---

#### `POST /api/submissions/`

* **Purpose:** Log metadata after successful Cloudinary upload
* **Permissions:** Public
* **Body:**

```json
{
  "prompt": 1,
  "image_url": "https://res.cloudinary.com/.../image.jpg",
  "public_id": "bangla_ocr_handwriting_data/..."
}
```

---

#### `GET /api/moderator/pending/`

* **Purpose:** View unreviewed submissions for moderation
* **Permissions:** Admin only
* **Returns:** List of pending entries with image URLs and prompts

---

#### `PUT /api/moderator/review/<int:id>/`

* **Purpose:** Mark a submission as "verified" or "rejected", with optional notes
* **Permissions:** Admin only
* **Example Update:**

```json
{
  "status": "verified",
  "notes": "Clear handwriting."
}
```

---

#### `GET /api/download/verified-submissions/`

* **Purpose:** Download a `.zip` with:

  * Folder of verified images
  * `labels.csv` (image → prompt mapping)
* **Permissions:** Admin only

---

## 🎨 Frontend: Vanilla JavaScript SPA

The frontend offers a minimal and intuitive experience for users contributing handwritten Bangla samples.

### 🔄 Flow Summary

1. **Fetch Prompt**

   * Calls `/api/prompt/` and displays it using typewriter animation.

2. **Select & Preview Image**

   * Users upload an image which is locally previewed on-screen.

3. **Upload & Submit**

   * Fetch secure Cloudinary signature from `/api/cloudinary-config/`
   * Upload image directly to Cloudinary
   * Send metadata to `/api/submissions/` for logging

4. **Live Feedback**

   * Users see real-time status updates:
     `CONNECTING... → TRANSMITTING... → DONE ✅`

---

## 🚀 Future: Admin Moderation Dashboard

Currently, moderation is done via API tools (like Postman). A future admin frontend is planned with:

### Planned Features

* 🔐 Login-authenticated admin interface
* 📋 View & moderate pending submissions
* ✅ Approve/Reject entries with image preview
* 📥 One-click dataset export (.zip + labels.csv)
* 📊 Submission analytics dashboard
* 🛠 Built with React or Vue for responsiveness

---

## 📁 Dataset Export Format

```
verified_dataset.zip
├── images/
│   ├── user1_image.jpg
│   └── user2_image.jpg
└── labels.csv

# labels.csv format:
filename,text
user1_image.jpg,বাংলা আমার মাতৃভাষা।
user2_image.jpg,আমার সোনার বাংলা...
```

---

## 🛠️ Tech Stack

| Layer    | Technology           |
| -------- | -------------------- |
| Backend  | Django + DRF         |
| Frontend | HTML, CSS, JS        |
| Cloud    | Cloudinary (uploads) |
| Auth     | Django Admin         |
| Dataset  | .zip + CSV export    |

---

## 🙌 Contributing

Pull requests are welcome! If you plan on introducing breaking changes, please open an issue first to discuss the proposal.

---

## 📄 License

MIT License © RONY

---

