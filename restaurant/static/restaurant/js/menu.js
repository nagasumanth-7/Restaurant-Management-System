const menuItems = [
  ["starters", "Pesarattu", "Crispy whole green gram crepe, served with spicy allam (ginger) chutney and coconut relish", "₹ 140", true],
  ["starters", "Andhra Chicken 65", "Crispy boneless tender chicken morsels, tossed in curry leaves, garlic, and crushed Guntur chilli", "₹ 290", true],
  ["starters", "Gongura Kodi Vepudu", "Succulent pan-roasted chicken infused with tangy sorrel leaves and freshly pounded peppercorns", "₹ 320", true],
  ["tiffins", "Mini Tiffin Royal Combo", "Steamed melting idlis, crisp medu vada, homestyle sambar, and three artisanal coastal chutneys", "₹ 190", true],
  ["tiffins", "Ghee Podi Plain Dosa", "Golden crisp dosa roasted in pure country ghee and coated with fiery spiced lentil gunpowder", "₹ 130", true],
  ["tiffins", "Onion Rava Masala Dosa", "Lacy semolina dosa studded with green chillies, cracked cumin, spiced potato mash, and chutneys", "₹ 180", true],
  ["curries", "Andhra Mudda Pappu & Avakaya", "Velvety slow-simmered toor dal with homemade spicy mango pickle and hot melted cow ghee", "₹ 180", true],
  ["curries", "Paneer Butter Masala", "Hand-crafted cottage cheese cubes simmered in rich cashew, slow-cooked tomato, and kasuri methi", "₹ 260", true],
  ["curries", "Kodi Kura (Country Chicken Curry)", "Traditional rustic Andhra chicken curry bursting with roasted coriander, poppy seeds, and cloves", "₹ 340", true],
  ["rice", "Bagara Rice & Dalcha", "Fragrant cumin and whole-spice tempered basmati rice, paired with slow-cooked tamarind lentil stew", "₹ 210", true],
  ["rice", "Traditional Sambar Sadam", "Hearty comfort rice cooked together with drumstick sambar, shallots, ghee, and crisp appalam", "₹ 190", true],
  ["rice", "Nizami Dum Biryani", "Aromatic long-grain basmati, layered with marinated spices, saffron-infused milk, and caramelized onions", "₹ 280", true],
  ["beverages", "Degree Filter Coffee", "First-decoction South Indian roasted chicory coffee, frothed to perfection in brass davarah", "₹ 80", true],
  ["beverages", "Spiced Majjiga (Buttermilk)", "Chilled churned curd spiced with crushed ginger, green chilli, fresh mint, and roasted cumin", "₹ 70", true],
  ["beverages", "Rose Cardamom Lassi", "Thick artisan curd whipped with organic rose petal preserve and freshly crushed cardamom", "₹ 100", true],
];

const itemsContainer = document.querySelector("#items");
const searchInput = document.querySelector("#search");
let activeFilter = "all";

function renderMenu() {
  const searchText = searchInput ? searchInput.value.toLowerCase().trim() : "";
  const visibleItems = menuItems.filter((item) => {
    const matchesFilter = activeFilter === "all" || item[0] === activeFilter;
    const matchesSearch = (item[1] + " " + item[2]).toLowerCase().includes(searchText);
    return matchesFilter && matchesSearch;
  });

  if (!visibleItems.length) {
    itemsContainer.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 48px 24px; text-align: center; background: rgba(8, 22, 44, 0.4); border: 1px dashed rgba(121, 202, 255, 0.2); border-radius: 16px;">
        <p style="color: var(--text-muted); font-size: 15px; margin: 0;">No culinary creations match your search for "${searchText}".</p>
      </div>
    `;
    return;
  }

  const html = visibleItems.map((item) => {
    const availability = item[4] ? "AVAILABLE TODAY" : "PRE-ORDER ONLY";
    const unavailableClass = item[4] ? "" : "off";

    return `
      <article class="item card-3d ${unavailableClass}">
        <div class="top">
          <b>${item[1]}</b>
          <b>${item[3]}</b>
        </div>
        <p>${item[2]}</p>
        <div class="tag">
          <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background: ${item[4] ? '#75fff0' : '#888'};"></span>
          ${availability}
        </div>
      </article>
    `;
  }).join("");

  itemsContainer.innerHTML = html;
}

if (searchInput) {
  searchInput.addEventListener("input", renderMenu);
}

const filtersContainer = document.querySelector("#filters");
if (filtersContainer) {
  filtersContainer.addEventListener("click", (event) => {
    const selectedButton = event.target.closest("button");
    if (!selectedButton || !selectedButton.dataset.f) return;

    filtersContainer.querySelectorAll("button").forEach(btn => btn.classList.remove("active"));
    selectedButton.classList.add("active");
    activeFilter = selectedButton.dataset.f;
    renderMenu();
  });
}

renderMenu();
