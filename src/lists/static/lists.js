console.log("lists.js loading");
const initialize = (inputSelector, errorSelector) => {
  console.log("initialize called");
  const textInput = document.querySelector("#id_text");
  textInput.oninput = () => {
    const errorMsg = document.querySelector(".invalid-feedback");
    errorMsg.style.display = "none";
  };
};
