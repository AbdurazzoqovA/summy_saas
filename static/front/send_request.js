function renderMarkdown() {
  var markdownContent = document.getElementById("markdown-content").innerText;
  var htmlContent = marked.parse(markdownContent);
  document.getElementById("markdown-content").innerHTML = htmlContent;
}
function decodeHtml(html) {
  return html.replace(/&lt;/g, "<").replace(/&gt;/g, ">");
}

document.addEventListener("DOMContentLoaded", function () {
  const summaryButton = document.getElementById("summaryButton");
  const neighbourPanel = document.querySelector(".neighbourPanel");
  const resizablePanel = document.querySelector(".resizablePanel");
  const spinner = document.getElementById("summary-spinner");

  // Function to get CSRF token from the meta tag
  function getCsrfToken() {
    return document
      .querySelector('meta[name="csrf-token"]')
      .getAttribute("content");
  }

  summaryButton.addEventListener("click", function () {
    const text = neighbourPanel.textContent || neighbourPanel.innerText;
    // get button which has selected attribute
    let mode = document.querySelector(".mode-button[selected]").innerText;
    let rangeValue = 0;
    if (mode == "Paragraph") {
      rangeValue = document.getElementById("summary-length").value;
    }
    const data = { text: text, mode: mode, rangeValue: rangeValue };
    // Show spinner and disable button
    spinner.style.display = "block";
    summaryButton.disabled = true;
    let alertError = document.getElementById("alertError");

    // Send POST request
    fetch("https://summarygenerator.io/summary/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          // If the response includes an error key, display it
          alertError.innerHTML = data.error; // Set the error message
          alertError.style.display = "block"; // Show the alert
        } else {
          // If the response is successful, update the resizablePanel
          alertError.style.display = "none";
          // let result = marked.marked(data.summary);
          resizablePanel.innerHTML = data?.summary; // Assuming the response has a "summary" key
        }
        const wordCountElements = document.querySelectorAll(
          "#word-count-summary"
        );
        const words = data.summary
          .trim()
          .split(/\s+/)
          .filter((w) => w);
        wordCountElements.forEach((el) => {
          el.innerHTML = `Words: ${words.length}`;
        });
      })
      .catch((error) => {
        console.error("Error:", error);
      })
      .finally(() => {
        // Hide spinner and enable button
        spinner.style.display = "none";
        summaryButton.disabled = false;
      });
  });
});
