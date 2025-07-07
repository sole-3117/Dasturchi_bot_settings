const userId = "6887251996";  // foydalanuvchi ID
let currentSnippetId = null;
let correctText = "";
let submitBtn = document.getElementById("submitBtn");
let textarea = document.getElementById("userInput");
let feedback = document.getElementById("feedback");

function loadSnippet() {
  fetch(`/get_snippet?user_id=${userId}`)
    .then(res => res.json())
    .then(data => {
      currentSnippetId = data.id;
      correctText = data.text;
      document.getElementById("original").textContent = correctText;
      textarea.value = data.written || "";
      updateFeedback();
    });
}

function updateFeedback() {
  const input = textarea.value;
  let result = "";
  let correct = true;

  for (let i = 0; i < correctText.length; i++) {
    const expected = correctText[i] || "";
    const typed = input[i] || "";

    if (expected === typed) {
      result += expected;
    } else if (typed) {
      result += `<span class="error">${expected}</span>`;
      correct = false;
    } else {
      result += expected;
    }
  }

  feedback.innerHTML = `<pre>${result}</pre>`;
  submitBtn.style.display = input.trim() === correctText.trim() ? "block" : "none";
}

textarea.addEventListener("input", updateFeedback);

submitBtn.addEventListener("click", () => {
  fetch("/submit_code", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      user_id: userId,
      snippet_id: currentSnippetId,
      written: textarea.value
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.correct) {
        alert("✅ To‘g‘ri yozdingiz!");
        textarea.disabled = true;
        submitBtn.disabled = true;
        setTimeout(() => {
          textarea.disabled = false;
          submitBtn.disabled = false;
          loadSnippet();  // yangi snippet yuklash
        }, 1500);
      } else {
        alert("❌ Xatolik bor. Davom eting.");
      }
    });
});

document.addEventListener("DOMContentLoaded", loadSnippet);