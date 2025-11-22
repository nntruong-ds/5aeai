// script.js - PHIÊN BẢN HOÀN CHỈNH ĐÃ CHỈNH SỬA
const API_URL = "/search";   // URL backend Flask

const chatBox = document.getElementById("chatBox");
const queryInput = document.getElementById("queryInput");
const imageUpload = document.getElementById("imageUpload");
const imagePreview = document.getElementById("imagePreview");
const sendBtn = document.getElementById("sendBtn");
const themeToggle = document.getElementById("themeToggle");
const clearBtn = document.getElementById("clearBtn");

let images = []; 
let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];

// ===== TEXTAREA AUTO RESIZE =====
queryInput.addEventListener('input', () => {
  queryInput.style.height = 'auto';
  queryInput.style.height = Math.min(queryInput.scrollHeight, 120) + 'px';
});

// ===== THEME TOGGLE =====
if (themeToggle) {
  const savedTheme = localStorage.getItem('theme') || 'dark';
  document.body.dataset.theme = savedTheme;

  themeToggle.addEventListener('click', () => {
    const current = document.body.dataset.theme;
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.body.dataset.theme = newTheme;
    localStorage.setItem('theme', newTheme);
  });
}

// ===== CLEAR HISTORY =====
if (clearBtn) {
  clearBtn.addEventListener('click', () => {
    if (confirm('Bạn có chắc muốn xóa toàn bộ lịch sử chat?')) {
      chatHistory = [];
      localStorage.removeItem('chatHistory');
      chatBox.innerHTML = '';
      showEmptyState();
    }
  });
}

// ===== EMPTY STATE =====
function showEmptyState() {
  const div = document.createElement('div');
  div.className = 'empty-state';
  div.innerHTML = `
    <h2>Xin chào! 👋</h2>
    <p>Tôi có thể giúp gì cho bạn hôm nay?</p>
  `;
  chatBox.appendChild(div);
}

// Load history
if (chatHistory.length === 0) {
  showEmptyState();
} else {
  chatHistory.forEach(msg => addMessage(msg.sender, msg.text, msg.images || [], false, msg.isMarkdown));
}

// ===== Read file → Base64 =====
function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve({ file: file, dataURL: reader.result });
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
}

// ===== Paste image support =====
document.addEventListener("paste", async (e) => {
  const items = e.clipboardData?.items;
  if (!items) return;

  const filePromises = [];

  for (const item of items) {
    if (item.kind === "file" && item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (file) filePromises.push(readFileAsDataURL(file));
    }
  }

  if (filePromises.length > 0) {
    e.preventDefault();
    const newImages = await Promise.all(filePromises);
    images = images.concat(newImages).slice(0, 5);
    updatePreview();
  }
});

// ===== Upload selected image =====
imageUpload.addEventListener("change", async () => {
  const files = Array.from(imageUpload.files);
  const filePromises = files.map(readFileAsDataURL);

  const newImages = await Promise.all(filePromises);
  images = images.concat(newImages).slice(0, 5);

  updatePreview();
  imageUpload.value = "";
});

// ===== Remove uploaded preview =====
imagePreview.addEventListener("click", (e) => {
  if (e.target.tagName === "BUTTON") {
    const idx = parseInt(e.target.dataset.idx);
    images.splice(idx, 1);
    updatePreview();
  }
});

// ===== Update preview =====
function updatePreview() {
  imagePreview.innerHTML = "";
  images.forEach((imgData, i) => {
    const div = document.createElement("div");
    div.className = "preview-item";
    div.innerHTML = `
      <img src="${imgData.dataURL}" alt="preview" />
      <button data-idx="${i}">×</button>
    `;
    imagePreview.appendChild(div);
  });
}

// ===== SEND MESSAGE =====
async function sendMessage() {
  const text = queryInput.value.trim();
  if (!text && images.length === 0) return;

  const emptyState = chatBox.querySelector('.empty-state');
  if (emptyState) emptyState.remove();

  const tempImages = [...images];

  // Display user message
  addMessage("user", text, tempImages.map(img => img.dataURL));

  queryInput.value = "";
  queryInput.style.height = 'auto';
  images = [];
  updatePreview();

  sendBtn.disabled = true;

  // Display typing indicator
  const loadingMsg = addMessage("bot", "", [], true);

  // Prepare payload
  const fd = new FormData();
  fd.append("query", text);
  tempImages.forEach(img => fd.append("file", img.file));

  try {
    const res = await fetch("http://127.0.0.1:8000/api/predict-image", {
      method: "POST",
      body: fd
    });


    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || `Lỗi ${res.status}`);
    }

    const data = await res.json();

    chatBox.removeChild(loadingMsg);

    // Display bot response (text + images base64)
    addMessage("bot", data.text, data.images || [], false, true);

  } catch (error) {
    chatBox.removeChild(loadingMsg);
    addMessage("bot", `Lỗi kết nối: ${error.message}`);
  } finally {
    sendBtn.disabled = false;
  }
}

// ===== Bind send events =====
sendBtn.addEventListener("click", sendMessage);

queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// ===== Lightbox for images =====
function openLightbox(url) {
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightboxImg');
  lightboxImg.src = url;
  lightbox.classList.add('active');
}

const lightbox = document.getElementById('lightbox');
const lightboxClose = document.getElementById('lightboxClose');

lightboxClose.onclick = () => lightbox.classList.remove('active');
lightbox.onclick = (e) => { if (e.target === lightbox) lightbox.classList.remove('active'); };

// ===== Copy text =====
function copyText(text) {
  const plainText = text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1');

  navigator.clipboard.writeText(plainText);

  const n = document.createElement('div');
  n.textContent = 'Đã copy!';
  n.style.cssText = 'position:fixed;top:20px;right:20px;background:#10b981;color:white;padding:12px 20px;border-radius:8px;z-index:9999;';
  document.body.appendChild(n);
  setTimeout(() => n.remove(), 2000);
}

// ===== Add message to chat =====
function addMessage(sender, text, imgUrls = [], isTyping = false, isMarkdown = false) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = sender === "user" ? "B" : "AI";
  div.appendChild(avatar);

  const content = document.createElement("div");
  content.className = "message-content";

  if (text) {
    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = isMarkdown ? marked.parse(text) : text;
    content.appendChild(bubble);
  }

  if (imgUrls.length > 0) {
    const imgsDiv = document.createElement("div");
    imgsDiv.className = "message-images";
    imgUrls.forEach(url => {
      const imgDiv = document.createElement("div");
      imgDiv.className = "message-image";
      const img = new Image();
      img.src = url;
      img.loading = "lazy";
      img.style.cursor = "pointer";
      img.onclick = () => openLightbox(url);
      imgDiv.appendChild(img);
      imgsDiv.appendChild(imgDiv);
    });
    content.appendChild(imgsDiv);
  }

  if (isTyping) {
    const typing = document.createElement("div");
    typing.className = "typing";
    typing.innerHTML = "<span></span><span></span><span></span>";
    content.appendChild(typing);
  }

  if (sender === "bot" && text && !isTyping) {
    const actions = document.createElement("div");
    actions.className = "message-actions";
    actions.innerHTML = `<button class="action-btn copy-btn">📋 Copy</button>`;
    actions.querySelector('.copy-btn').onclick = () => copyText(text);
    content.appendChild(actions);
  }

  div.appendChild(content);
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (!isTyping) {
    chatHistory.push({ sender, text, images: imgUrls, isMarkdown });
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory.slice(-200)));
  }

  return div;
}
