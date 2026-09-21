const menuItems = [
  ["starters", "Pesarattu", "Green gram dosa, ginger chutney, allam chutney", "₹ 120", true],
  ["starters", "Andhra Chicken 65", "Crispy boneless chicken, red chilli, curry leaves", "₹ 260", true],
  ["starters", "Gongura Chicken", "Tangy sorrel gravy, roasted chilli, garlic", "₹ 290", true],
  ["tiffins", "Mini Tiffin Combo", "Idli, medu vada, sambar, coconut chutney", "₹ 180", true],
  ["tiffins", "Plain Dosa", "Golden crisp dosa, podi, gunpowder, sambar", "₹ 110", true],
  ["tiffins", "Onion Rava Masala Dosa", "Semolina dosa, onions, potato masala, chutneys", "₹ 165", true],
  ["curries", "Andhra Pappu", "Toor dal, tamarind, chilli, garlic tempering", "₹ 160", true],
  ["curries", "Paneer Butter Masala", "Soft paneer cubes, rich cashew tomato gravy", "₹ 240", true],
  ["curries", "Aavakaaya Kodi Curry", "Traditional mango pickle chicken curry", "₹ 320", true],
  ["rice", "Tomato Rice", "Flavoured rice with tomato, mustard, curry leaves", "₹ 170", true],
  ["rice", "Sambar Rice", "Comfort rice, sambar, ghee, pappad", "₹ 180", true],
  ["rice", "Veg Biryani", "Aromatic rice, vegetables, mint, biryani spices", "₹ 220", true],
  ["beverages", "Filter Coffee", "South Indian brewed coffee with froth", "₹ 70", true],
  ["beverages", "Buttermilk", "Fresh curd buttermilk, cumin, mint", "₹ 60", true],
  ["beverages", "Sweet Lassi", "Yogurt, rose, sugar, cardamom", "₹ 90", true],
];

const itemsContainer = document.querySelector("#items");
const searchInput = document.querySelector("#search");
let activeFilter = "all";

function renderMenu() {
  const searchText = searchInput.value.toLowerCase();
  const visibleItems = menuItems.filter((item) => {
    const matchesFilter = activeFilter === "all" || item[0] === activeFilter;
    const matchesSearch = (item[1] + item[2]).toLowerCase().includes(searchText);
    return matchesFilter && matchesSearch;
  });

  const html = visibleItems.map((item) => {
    const availability = item[4] ? "AVAILABLE TODAY" : "UNAVAILABLE TODAY";
    const unavailableClass = item[4] ? "" : "off";

    return '<article class="item ' + unavailableClass + '">' +
      '<div class="top">' +
      '<b>' + item[1] + '</b>' +
      '<b>' + item[3] + '</b>' +
      '</div>' +
      '<p>' + item[2] + '</p>' +
      '<small class="tag">● ' + availability + '</small>' +
      '</article>';
  }).join("");

  itemsContainer.innerHTML = html || "<p>No dishes match your search.</p>";
}

searchInput.addEventListener("input", renderMenu);

document.querySelector("#filters").addEventListener("click", (event) => {
  const selectedButton = event.target;

  if (!selectedButton.dataset.f) {
    return;
  }

  document.querySelector("#filters .active").classList.remove("active");
  selectedButton.classList.add("active");
  activeFilter = selectedButton.dataset.f;
  renderMenu();
});

renderMenu();
