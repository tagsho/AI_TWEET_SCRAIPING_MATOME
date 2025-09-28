const API_BASE = import.meta?.env?.VITE_API_BASE ?? "http://localhost:8000";

const state = {
  sort: "new",
  tag: "",
  keyword: "",
  sourceType: "",
};

const tabs = document.querySelectorAll(".tab");
const keywordInput = document.getElementById("keyword");
const tagInput = document.getElementById("tag");
const sourceTypeSelect = document.getElementById("sourceType");
const refreshButton = document.getElementById("refresh");
const cardsContainer = document.getElementById("items");
const cardTemplate = document.getElementById("card-template");

function buildQuery() {
  const params = new URLSearchParams();
  params.set("sort", state.sort);
  if (state.keyword) params.set("q", state.keyword);
  if (state.tag) params.set("tag", state.tag);
  if (state.sourceType) params.set("source_type", state.sourceType);
  return params.toString();
}

async function fetchItems() {
  const query = buildQuery();
  const response = await fetch(`${API_BASE}/items?${query}`);
  if (!response.ok) {
    console.error("API error", response.status);
    return [];
  }
  return response.json();
}

function createMentionNode(mention) {
  const wrapper = document.createElement("div");
  wrapper.className = "mention";
  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = `${mention.source_name} ${mention.source_handle ?? ""}`.trim();
  wrapper.appendChild(meta);
  if (mention.post_url && mention.source_type === "twitter") {
    const blockquote = document.createElement("blockquote");
    blockquote.className = "twitter-tweet";
    const link = document.createElement("a");
    link.href = mention.post_url;
    blockquote.appendChild(link);
    wrapper.appendChild(blockquote);
  } else if (mention.embed_html) {
    const div = document.createElement("div");
    div.innerHTML = mention.embed_html;
    wrapper.appendChild(div);
  } else if (mention.post_url) {
    const link = document.createElement("a");
    link.href = mention.post_url;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = "紹介ポストを見る";
    wrapper.appendChild(link);
  }
  const scoreLine = document.createElement("div");
  scoreLine.className = "scoreline";
  const metrics = [];
  if (mention.like_count) metrics.push(`❤ ${mention.like_count}`);
  if (mention.repost_count) metrics.push(`🔁 ${mention.repost_count}`);
  if (mention.reply_count) metrics.push(`💬 ${mention.reply_count}`);
  scoreLine.textContent = metrics.join("  ");
  wrapper.appendChild(scoreLine);
  return wrapper;
}

function renderItems(items) {
  cardsContainer.innerHTML = "";
  items.forEach((item) => {
    const node = cardTemplate.content.firstElementChild.cloneNode(true);
    node.querySelector(".title").textContent = item.title ?? item.url;
    node.querySelector(".summary").textContent = item.summary ?? "要約準備中";
    node.querySelector(".score-value").textContent = `${item.score_buzz.toFixed(2)} / ${item.score_new.toFixed(2)}`;
    const pointsList = node.querySelector(".points");
    pointsList.innerHTML = "";
    item.summary_points.forEach((point) => {
      const li = document.createElement("li");
      li.textContent = point;
      pointsList.appendChild(li);
    });
    const tagsContainer = node.querySelector(".tags");
    tagsContainer.innerHTML = "";
    item.tags.forEach((tag) => {
      const span = document.createElement("span");
      span.textContent = tag;
      tagsContainer.appendChild(span);
    });
    const mentionsContainer = node.querySelector(".mentions");
    mentionsContainer.innerHTML = "";
    item.mentions.forEach((mention) => {
      mentionsContainer.appendChild(createMentionNode(mention));
    });
    const link = node.querySelector(".source-link");
    link.href = item.url;
    cardsContainer.appendChild(node);
  });
  if (window.twttr && window.twttr.widgets) {
    window.twttr.widgets.load();
  }
}

async function refresh() {
  const items = await fetchItems();
  renderItems(items);
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    state.sort = tab.dataset.sort;
    refresh();
  });
});

keywordInput.addEventListener("change", () => {
  state.keyword = keywordInput.value;
});

tagInput.addEventListener("change", () => {
  state.tag = tagInput.value;
});

sourceTypeSelect.addEventListener("change", () => {
  state.sourceType = sourceTypeSelect.value;
  refresh();
});

refreshButton.addEventListener("click", () => {
  state.keyword = keywordInput.value;
  state.tag = tagInput.value;
  refresh();
});

refresh();
