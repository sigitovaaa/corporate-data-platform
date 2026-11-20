from pathlib import Path
import duckdb
import networkx as nx

data_file = Path("data/raw/companies.csv")

if not data_file.is_file():
    raise FileNotFoundError("Не найден data/raw/companies.csv")

con = duckdb.connect()
companies = con.execute("""
    SELECT id, name, industry, city, employees
    FROM read_csv_auto('data/raw/companies.csv')
""").fetchall()
con.close()

G = nx.Graph()

for company_id, name, industry, city, employees in companies:
    company_node = f"company:{company_id}"
    city_node = f"city:{city}"
    industry_node = f"industry:{industry}"

    G.add_node(
        company_node,
        node_type="company",
        label=name,
        employees=employees
    )

    G.add_node(
        city_node,
        node_type="city",
        label=city
    )

    G.add_node(
        industry_node,
        node_type="industry",
        label=industry
    )

    G.add_edge(company_node, city_node)
    G.add_edge(company_node, industry_node)

print("Количество организаций в CSV:", len(companies))
print("Количество вершин графа:", G.number_of_nodes())
print("Количество рёбер графа:", G.number_of_edges())

print("\nОрганизации:")
for node, data in G.nodes(data=True):
    if data["node_type"] == "company":
        print(data["label"], "-", data["employees"], "сотрудников")

print("\nГорода:")
for node, data in G.nodes(data=True):
    if data["node_type"] == "city":
        print(data["label"])

print("\nОтрасли:")
industries = sorted(
    data["label"]
    for _, data in G.nodes(data=True)
    if data["node_type"] == "industry"
)
for industry in industries:
    print(industry)

company_nodes = [node for node, data in G.nodes(data=True)
    if data["node_type"] == "company"]

if company_nodes:
    selected_company = company_nodes[0]
    print("\nСвязи организации:")
    print(G.nodes[selected_company]["label"])
    for neighbor in G.neighbors(selected_company):
        print("-", G.nodes[neighbor]["label"], "(", G.nodes[neighbor]["node_type"], ")")

print("\nОрганизации по городам:")
for node, data in G.nodes(data=True):
    if data["node_type"] == "city":
        companies_in_city = [G.nodes[neighbor]["label"]
            for neighbor in G.neighbors(node)
            if G.nodes[neighbor]["node_type"] == "company"]
        print(data["label"], ":", ", ".join(companies_in_city))

print("\nОрганизации по отраслям:")
for node, data in G.nodes(data=True):
    if data["node_type"] == "industry":
        organizations = [G.nodes[neighbor]["label"]
            for neighbor in G.neighbors(node)
            if G.nodes[neighbor]["node_type"] == "company"]
        print(data["label"], ":", ", ".join(organizations))

print("\nОбщие города и отрасли:")
for i in range(len(company_nodes)):
    for j in range(i + 1, len(company_nodes)):
        first = company_nodes[i]
        second = company_nodes[j]
        common = (set(G.neighbors(first)) & set(G.neighbors(second)))
        if common:
            print(G.nodes[first]["label"], "<->", G.nodes[second]["label"])
            for node in common:
                print("Общий объект:", G.nodes[node]["label"])

print("\nСтепени вершин:")
for node, degree in G.degree():
    print(G.nodes[node]["label"],  "-", degree)

ranking = sorted(G.degree(), key=lambda item: item[1], reverse=True)
print("\nНаиболее связанные вершины:")
for node, degree in ranking[:5]:
    print(G.nodes[node]["label"], "-", degree)

degree_centrality = nx.degree_centrality(G)
print("\nЦентральность по степени:")
for node, value in sorted(
    degree_centrality.items(),
    key=lambda item: item[1],
    reverse=True)[:5]:
    print(G.nodes[node]["label"], "-", round(value, 3))

betweenness = nx.betweenness_centrality(G)
print("\nПосредническая центральность:")
for node, value in sorted(
    betweenness.items(),
    key=lambda item: item[1],
    reverse=True)[:5]:
    print(G.nodes[node]["label"], "-", round(value, 3))

components = list(nx.connected_components(G))
print("\nКоличество компонент связности:")
print(len(components))
for index, component in enumerate(components, start=1):
    print(f"Компонента {index}:", len(component), "вершин")

if len(company_nodes) >= 2:
    source = company_nodes[0]
    target = company_nodes[1]
    if nx.has_path(G, source, target): 
       path = nx.shortest_path(G, source=source, target=target)
       print("\nКратчайший путь:")
       for node in path:
            print(G.nodes[node]["label"])
    else:
        print("\nМежду выбранными организациями " "нет пути")

# ==========================================================
# 13. Определение ключевых характеристик графа
# ==========================================================

def count_companies(node):
    """Число соседей-компаний у вершины (город или отрасль)."""
    return sum(
        1 for n in G.neighbors(node)
        if G.nodes[n]["node_type"] == "company"
    )

print("\n" + "=" * 50)
print("13. АНАЛИЗ ГРАФА")
print("=" * 50)

# --- 13.1 Город с наибольшим количеством связанных организаций ---
city_nodes = [n for n, d in G.nodes(data=True) if d["node_type"] == "city"]
if city_nodes:
    top_city = max(city_nodes, key=count_companies)
    top_city_count = count_companies(top_city)
    print("\n13.1. Город с наибольшим количеством организаций:")
    print(f"  {G.nodes[top_city]['label']} — {top_city_count} организаций")
else:
    top_city_count = 0
    print("\n13.1. В графе нет вершин-городов.")

# --- 13.2 Отрасль с наибольшим количеством организаций ---
industry_nodes = [n for n, d in G.nodes(data=True) if d["node_type"] == "industry"]
if industry_nodes:
    top_industry = max(industry_nodes, key=count_companies)
    top_industry_count = count_companies(top_industry)
    print("\n13.2. Отрасль с наибольшим количеством организаций:")
    print(f"  {G.nodes[top_industry]['label']} — {top_industry_count} организаций")
else:
    top_industry_count = 0
    print("\n13.2. В графе нет вершин-отраслей.")

# --- 13.3 Вершина с максимальной посреднической центральностью ---
betweenness = nx.betweenness_centrality(G)
top_betweenness_node = max(betweenness, key=betweenness.get)
print("\n13.3. Вершина с максимальной посреднической центральностью:")
print(
    f"  {G.nodes[top_betweenness_node]['label']} "
    f"(тип: {G.nodes[top_betweenness_node]['node_type']}, "
    f"betweenness = {betweenness[top_betweenness_node]:.4f})"
)

# --- 13.4 Количество компонент связности ---
components = list(nx.connected_components(G))
print("\n13.4. Количество компонент связности:", len(components))
for index, component in enumerate(components, start=1):
    print(f"  Компонента {index}: {len(component)} вершин")

# --- 13.5 Существование пути между двумя выбранными организациями ---
print("\n13.5. Существование пути между двумя организациями:")
if len(company_nodes) >= 2:
    source = company_nodes[0]
    target = company_nodes[1]
    has_path = nx.has_path(G, source, target)
    print(f"  {G.nodes[source]['label']} -> {G.nodes[target]['label']}: {has_path}")
    if has_path:
        path = nx.shortest_path(G, source=source, target=target)
        print("  Кратчайший путь:", " -> ".join(G.nodes[n]["label"] for n in path))
else:
    has_path = False
    print("  В графе меньше двух организаций — путь проверить нельзя.")

# ==========================================================
# 14. Интерпретация результатов
# ==========================================================

print("\n" + "=" * 50)
print("14. ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ")
print("=" * 50)

if city_nodes:
    print(
        f"\n14.1. Город «{G.nodes[top_city]['label']}» — центр деловой активности: "
        f"в нём сосредоточено {top_city_count} организаций из датасета. "
        f"В графе это город-хаб с максимальной степенью среди городов; "
        f"через него проходит больше всего связей «компания — город»."
    )

if industry_nodes:
    print(
        f"\n14.2. Отрасль «{G.nodes[top_industry]['label']}» — самая массовая сфера "
        f"деятельности: {top_industry_count} организаций. "
        f"Это отраслевой хаб, связывающий наибольшее число компаний."
    )

print(
    f"\n14.3. Вершина «{G.nodes[top_betweenness_node]['label']}» "
    f"(тип: {G.nodes[top_betweenness_node]['node_type']}) имеет максимальную "
    f"посредническую центральность ({betweenness[top_betweenness_node]:.4f}). "
    f"Это значит, что она чаще других лежит на кратчайших путях между "
    f"компаниями и работает как «мост»: её удаление сильнее всего увеличит "
    f"расстояния между организациями и может раздробить граф."
)

print(
    f"\n14.4. Компонент связности: {len(components)}. "
    + (
        "Граф связный — все компании так или иначе связаны через общие города "
        "и отрасли."
        if len(components) == 1
        else "В данных есть изолированные группы компаний, не имеющие общих "
             "городов или отраслей с остальными."
    )
)

if len(company_nodes) >= 2:
    if has_path:
        print(
            f"\n14.5. Между «{G.nodes[source]['label']}» и "
            f"«{G.nodes[target]['label']}» существует путь: компании связаны "
            f"через общие города/отрасли (прямо или транзитивно). "
            f"Кратчайший путь имеет длину {len(path) - 1} рёбер — это мера "
            f"их «близости» в графе."
        )
    else:
        print(
            f"\n14.5. Между «{G.nodes[source]['label']}» и "
            f"«{G.nodes[target]['label']}» пути нет: компании находятся в разных "
            f"компонентах связности и не имеют общих городов или отраслей даже "
            f"через промежуточные вершины."
        )
def get_graph():
    return G
