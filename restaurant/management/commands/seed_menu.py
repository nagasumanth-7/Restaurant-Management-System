from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from restaurant.models import MenuCategory, MenuItem


class Command(BaseCommand):
    help = "Seeds initial menu categories, items, and role groups into the database idempotently."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing restaurant database seed..."))

        # 1. Create Role Groups (Section 7)
        roles = ["CUSTOMER", "WAITER", "CHEF", "CASHIER", "MANAGER", "ADMIN"]
        for role_name in roles:
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Created Role Group: {role_name}"))

        # 2. Categories
        categories_data = [
            ("Starters", "Crisp, fiery, and appetizing South Indian and tandoor starters to awaken your palate."),
            ("Tiffins", "Traditional South Indian breakfast staples, golden dosas, and steamed idlis."),
            ("Curries", "Slow-simmered rich curries prepared with freshly roasted whole spices."),
            ("Rice & Biryani", "Aromatic long-grain basmati biryanis layered with delicate saffron and spices."),
            ("Beverages", "Refreshing handcrafted drinks, cooling buttermilk, and artisanal South Indian coffees."),
            ("Desserts", "Warm artisanal sweets and decadent post-meal delicacies."),
        ]

        cat_instances = {}
        for cat_name, cat_desc in categories_data:
            cat_obj, created = MenuCategory.objects.get_or_create(
                name=cat_name,
                defaults={"description": cat_desc, "is_active": True},
            )
            cat_instances[cat_name] = cat_obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Created Category: {cat_name}"))
            else:
                self.stdout.write(f"  = Existing Category: {cat_name}")

        # 3. Initial Menu Items (Section 5)
        menu_items_data = [
            # STARTERS
            {
                "category": "Starters",
                "name": "Pesarattu",
                "description": "Crispy whole green gram crepe, served with spicy allam (ginger) chutney and coconut relish.",
                "price": Decimal("140.00"),
                "preparation_time": 10,
            },
            {
                "category": "Starters",
                "name": "Andhra Chicken 65",
                "description": "Crispy boneless tender chicken morsels tossed in curry leaves, garlic, and crushed Guntur chilli.",
                "price": Decimal("290.00"),
                "preparation_time": 15,
            },
            {
                "category": "Starters",
                "name": "Paneer Tikka",
                "description": "Smoky tandoor-charred cottage cheese cubes marinated in aromatic spices and hung curd.",
                "price": Decimal("240.00"),
                "preparation_time": 15,
            },
            {
                "category": "Starters",
                "name": "Gobi Manchurian",
                "description": "Crisp cauliflower florets tossed in tangy Indo-Chinese garlic soy reduction.",
                "price": Decimal("210.00"),
                "preparation_time": 15,
            },

            # TIFFINS
            {
                "category": "Tiffins",
                "name": "Plain Dosa",
                "description": "Classic crisp golden rice-lentil crepe served with sambar and fresh coconut chutneys.",
                "price": Decimal("80.00"),
                "preparation_time": 8,
            },
            {
                "category": "Tiffins",
                "name": "Masala Dosa",
                "description": "Golden crisp crepe filled with spiced potato masala, paired with coastal chutneys.",
                "price": Decimal("120.00"),
                "preparation_time": 10,
            },
            {
                "category": "Tiffins",
                "name": "Idly",
                "description": "Steamed fluffy rice cakes served steaming hot with spiced lentil sambar and chutneys.",
                "price": Decimal("70.00"),
                "preparation_time": 8,
            },
            {
                "category": "Tiffins",
                "name": "Vada",
                "description": "Crisp golden fried medu vadas with a soft fluffy interior, served with coconut relish.",
                "price": Decimal("70.00"),
                "preparation_time": 8,
            },

            # CURRIES
            {
                "category": "Curries",
                "name": "Butter Chicken",
                "description": "Tender chicken cooked in rich satin tomato, cashew butter gravy, and dried fenugreek leaves.",
                "price": Decimal("280.00"),
                "preparation_time": 20,
            },
            {
                "category": "Curries",
                "name": "Paneer Butter Masala",
                "description": "Hand-crafted cottage cheese cubes simmered in a velvety tomato-cashew butter sauce.",
                "price": Decimal("240.00"),
                "preparation_time": 20,
            },
            {
                "category": "Curries",
                "name": "Andhra Chicken Curry",
                "description": "Traditional rustic country chicken curry bursting with roasted coriander, poppy seeds, and cloves.",
                "price": Decimal("290.00"),
                "preparation_time": 25,
            },
            {
                "category": "Curries",
                "name": "Dal Tadka",
                "description": "Yellow lentils slow-cooked and tempered with garlic, cumin, whole red chillies, and pure ghee.",
                "price": Decimal("160.00"),
                "preparation_time": 15,
            },

            # RICE & BIRYANI
            {
                "category": "Rice & Biryani",
                "name": "Chicken Biryani",
                "description": "Aromatic long-grain basmati rice layered with succulent marinated chicken, saffron, and fried onions.",
                "price": Decimal("280.00"),
                "preparation_time": 25,
            },
            {
                "category": "Rice & Biryani",
                "name": "Mutton Biryani",
                "description": "Tender fall-off-the-bone mutton slow-cooked with spiced dum basmati rice and fresh mint.",
                "price": Decimal("350.00"),
                "preparation_time": 30,
            },
            {
                "category": "Rice & Biryani",
                "name": "Veg Biryani",
                "description": "Fragrant garden-fresh vegetables and basmati rice slow-dum cooked with whole ground spices.",
                "price": Decimal("220.00"),
                "preparation_time": 20,
            },

            # BEVERAGES
            {
                "category": "Beverages",
                "name": "Fresh Lime Soda",
                "description": "Sparkling chilled lime soda served sweet, salted, or mixed to order.",
                "price": Decimal("80.00"),
                "preparation_time": 5,
            },
            {
                "category": "Beverages",
                "name": "Mango Lassi",
                "description": "Thick creamy yogurt smoothie blended with luscious Alphonso mango pulp and cardamom.",
                "price": Decimal("100.00"),
                "preparation_time": 5,
            },
            {
                "category": "Beverages",
                "name": "Cold Coffee",
                "description": "Rich chilled espresso blended with velvety full-cream milk and a scoop of vanilla ice cream.",
                "price": Decimal("120.00"),
                "preparation_time": 7,
            },
            {
                "category": "Beverages",
                "name": "Mineral Water",
                "description": "Chilled packaged natural mineral water bottle.",
                "price": Decimal("30.00"),
                "preparation_time": 1,
            },

            # DESSERTS
            {
                "category": "Desserts",
                "name": "Gulab Jamun",
                "description": "Warm golden milk-solid dumplings soaked in fragrant cardamom saffron syrup.",
                "price": Decimal("110.00"),
                "preparation_time": 5,
            },
        ]

        items_created = 0
        items_existing = 0

        for item_data in menu_items_data:
            cat_obj = cat_instances[item_data["category"]]
            item_obj, created = MenuItem.objects.get_or_create(
                category=cat_obj,
                name=item_data["name"],
                defaults={
                    "description": item_data["description"],
                    "price": item_data["price"],
                    "preparation_time": item_data["preparation_time"],
                    "is_active": True,
                    "is_available": True,
                },
            )
            if created:
                items_created += 1
                self.stdout.write(self.style.SUCCESS(f"  + Added Menu Item: {item_obj.name} (₹{item_obj.price})"))
            else:
                items_existing += 1
                self.stdout.write(f"  = Existing Menu Item: {item_obj.name}")

        # 4. Initial Restaurant Tables
        tables_data = [
            ("T-01", 2, "WINDOW"),
            ("T-02", 2, "WINDOW"),
            ("T-03", 2, "WINDOW"),
            ("T-04", 4, "INDOOR"),
            ("T-05", 4, "INDOOR"),
            ("T-06", 4, "INDOOR"),
            ("T-07", 6, "INDOOR"),
            ("T-08", 6, "INDOOR"),
            ("T-09", 4, "TERRACE"),
            ("T-10", 4, "TERRACE"),
            ("T-11", 8, "BOOTH"),
            ("T-12", 8, "BOOTH"),
        ]

        from restaurant.models import RestaurantTable
        tables_created = 0
        for t_num, cap, area in tables_data:
            t_obj, created = RestaurantTable.objects.get_or_create(
                table_number=t_num,
                defaults={"capacity": cap, "floor_area": area, "status": "AVAILABLE", "is_active": True},
            )
            if created:
                tables_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeed completed successfully: {items_created} items created, {items_existing} items verified, {tables_created} tables created."
            )
        )


