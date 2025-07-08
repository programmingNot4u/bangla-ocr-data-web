// ✨ Typewriter animation for Bangla prompt
function typeWriterEffect(element, text, speed = 40) {
  let i = 0;
  element.textContent = '';
  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }
  type();
}

document.addEventListener('DOMContentLoaded', () => {
  // API endpoint configuration
  const API_BASE_URL = 'https://hossainimamrony71.pythonanywhere.com/api'; // Production API endpoint

  // Get all necessary DOM elements
  const animatedPrompt = document.getElementById('animated-prompt');
  const fileUpload = document.getElementById('file-upload');
  const uploadForm = document.getElementById('upload-form');
  const submitBtn = document.querySelector('.submit-btn');
  const imagePreviewContainer = document.getElementById('image-preview-container');
  const imagePreview = document.getElementById('image-preview');
  const previewText = document.querySelector('.preview-text');
  const statusText = document.getElementById('status-text');
  const fileUploadLabelText = document.querySelector('.custom-file-upload .text');
  
  // Variable to store the current prompt ID from the API
  let currentPromptId = null;

  // --- 1. FETCH PROMPT FROM API ON PAGE LOAD ---
  async function fetchNewPrompt() {
    try {
      statusText.textContent = 'CONNECTING TO UPLINK...';
      statusText.className = 'status-progress';
      
      const response = await fetch(`${API_BASE_URL}/prompt/`);
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.statusText}`);
      }
      
      const data = await response.json();
      currentPromptId = data.id; // Store the prompt ID
      
      // Start the typewriter animation with the fetched prompt
      typeWriterEffect(animatedPrompt, data.text, 35);
      statusText.textContent = 'AWAITING INPUT';
      statusText.className = 'status-neutral';

    } catch (error) {
      console.error('Failed to fetch prompt:', error);
      animatedPrompt.textContent = 'সংযোগ স্থাপন করা যায়নি। অনুগ্রহ করে পৃষ্ঠাটি পুনরায় লোড করুন।';
      statusText.textContent = 'CONNECTION FAILED';
      statusText.className = 'status-error';
    }
  }
  
  // Initial prompt fetch
  fetchNewPrompt();

  // --- 2. HANDLE FILE PREVIEW ---
  fileUpload.addEventListener('change', () => {
    const file = fileUpload.files[0];
    if (file) {
      const reader = new FileReader();

      imagePreviewContainer.classList.add('active');
      previewText.style.display = 'none';
      imagePreview.style.display = 'block';

      reader.onload = function (e) {
        imagePreview.src = e.target.result;
      };
      reader.readAsDataURL(file);

      submitBtn.disabled = false;
      statusText.textContent = 'File selected. Awaiting transmission...';
      statusText.className = 'status-progress';
      fileUploadLabelText.textContent = 'File Loaded';
    }
  });

  // --- 3. HANDLE FORM SUBMISSION TO API ---
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (fileUpload.files.length === 0 || !currentPromptId) {
        statusText.textContent = 'ERROR: No file selected or no mission loaded.';
        statusText.className = 'status-error';
        return;
    }

    // Disable button and update status during upload
    submitBtn.disabled = true;
    submitBtn.textContent = 'UPLINKING...';
    statusText.textContent = 'Requesting upload permission...';
    statusText.className = 'status-progress';

    try {
        // --- STEP 1: Get signature and config from your backend ---
        const configResponse = await fetch(`${API_BASE_URL}/cloudinary-config/`);
        if (!configResponse.ok) {
            throw new Error('Could not get upload credentials from server.');
        }
        const config = await configResponse.json();
        
        // --- STEP 2: Prepare FormData and upload directly to Cloudinary ---
        statusText.textContent = 'Permission granted. Transmitting data to Cloudinary...';
        const imageFile = fileUpload.files[0];
        const formDataCloudinary = new FormData();

        formDataCloudinary.append('file', imageFile);
        formDataCloudinary.append('api_key', config.api_key);
        formDataCloudinary.append('timestamp', config.timestamp);
        formDataCloudinary.append('signature', config.signature);
        formDataCloudinary.append('folder', 'chrono_scribe_submissions'); // Must match folder in backend signature

        const cloudinaryUrl = `https://api.cloudinary.com/v1_1/${config.cloud_name}/image/upload`;

        const cloudinaryResponse = await fetch(cloudinaryUrl, {
            method: 'POST',
            body: formDataCloudinary,
        });

        if (!cloudinaryResponse.ok) {
            const errorData = await cloudinaryResponse.json();
            throw new Error(`Cloudinary upload failed: ${errorData.error.message}`);
        }
        
        const cloudinaryData = await cloudinaryResponse.json();
        const imageUrl = cloudinaryData.secure_url;
        const publicId = cloudinaryData.public_id;

        // --- STEP 3: Send the Cloudinary URL and public_id to your backend ---
        statusText.textContent = 'Data received by Cloudinary. Logging submission...';
        
        const backendPayload = {
            prompt: currentPromptId,
            image_url: imageUrl,
            public_id: publicId
        };
        
        const backendResponse = await fetch(`${API_BASE_URL}/submissions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(backendPayload),
        });

        if (!backendResponse.ok) {
            const errorData = await backendResponse.json();
            // Try to find a meaningful error message
            const message = errorData.detail || JSON.stringify(errorData);
            throw new Error(`Server submission failed: ${message}`);
        }

        // --- STEP 4: Success! ---
        statusText.textContent = 'Transmission complete. Thank you, contributor.';
        statusText.className = 'status-success';
        submitBtn.textContent = 'SENT';
        console.log('✅ Submission successfully logged.');

        setTimeout(() => {
            location.reload();
        }, 2000);

    } catch (error) {
        console.error('Submission failed:', error);
        statusText.textContent = `TRANSMISSION FAILED: ${error.message}`;
        statusText.className = 'status-error';
        submitBtn.disabled = false;
        submitBtn.textContent = 'RE-TRANSMIT';
    }
});
});