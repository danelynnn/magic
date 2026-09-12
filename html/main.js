console.log("hi");

window.addEventListener("load", (event) => {
  const list = document.getElementById("list");

  fetch("http://localhost:8000/out/TLA.json")
    .then((response) => response.json())
    .then((json) => {
      for (category of Object.keys(json)) {
        const header = document.createElement("h2");
        header.textContent = category;
        header.id = category;
        list.appendChild(header);

        const section = document.createElement("div");
        section.style = "display: flex; flex-wrap: wrap; gap: 10px";

        for (card of json[category]) {
          const item = document.createElement("div");

          const title = document.createElement("p");
          title.textContent = card.title;
          item.appendChild(title);

          const img = document.createElement("img");
          img.setAttribute("src", card.src);
          img.setAttribute("height", "300px");
          item.appendChild(img);
          const img2 = document.createElement("img");
          img2.setAttribute("src", card.src2);
          img2.setAttribute("height", "300px");
          item.appendChild(img2);

          section.appendChild(item);
        }

        list.appendChild(section);
      }
    });
});
