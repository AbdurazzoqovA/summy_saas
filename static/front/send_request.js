function renderMarkdown() {
  var markdownContent = document.getElementById("markdown-content").innerText;
  var htmlContent = marked.parse(markdownContent);
  document.getElementById("markdown-content").innerHTML = htmlContent;
}
function decodeHtml(html) {
  return html.replace(/&lt;/g, "<").replace(/&gt;/g, ">");
}

function converToBullets(text) {
  var textContent = text.trim();
  var lines = textContent.split("\n");

  // Create a new ul element
  var ulElement = document.createElement("ul");

  // Iterate through each line and create a li element for each
  lines.forEach(function (line) {
    var liElement = document.createElement("li");
    liElement.textContent = line.trim().substring(1); // Exclude the leading '-'
    ulElement.appendChild(liElement);
  });

  return ulElement;
}

document.addEventListener("DOMContentLoaded", function () {
  const summaryButton = document.getElementById("summaryButton");
  const neighbourPanel = document.querySelector(".neighbourPanel");
  const resizablePanel = document.querySelector(".resizablePanel");
  const spinner = document.getElementById("summary-spinner");
  console.log("21");
  // Function to get CSRF token from the meta tag
  function getCsrfToken() {
    return document
      .querySelector('meta[name="csrf-token"]')
      .getAttribute("content");
  }

  function requestforSummary(text) {
    // get button which has selected attribute
    let mode = document.querySelector(".mode-button[selected]").innerText;
    let rangeValue = 0;
    if (mode == "Paragraph") {
      rangeValue = document.getElementById("summary-length").value;
    }
    const data = { text: text, mode: mode, rangeValue: rangeValue };

    console.log(mode);
    // Show spinner and disable button
    spinner.style.display = "block";
    summaryButton.disabled = true;
    let alertError = document.getElementById("alertError");

    // Send POST request
    fetch("https://summarygenerator.io/en/summary/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);

        let btext = converToBullets(data.summary);
        console.log(btext);

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
  }

  summaryButton.addEventListener("click", function () {
    const text = neighbourPanel.textContent || neighbourPanel.innerText;

    var wordCount = text.split(/\s+/).filter(function (word) {
      return word.length > 0;
    }).length;
    console.log("Counting-Words", wordCount);

    var wordLimit = 800;

    if (wordCount <= wordLimit) requestforSummary(text);
    else {
      // document.getElementById("upgradePopup").style.display = "block";
      alert("Word Limit Exceeded! Upgrade to Pro for more features");
    }
  });
});
