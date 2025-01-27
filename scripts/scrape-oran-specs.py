from bs4 import BeautifulSoup
import json
import wget
import pathlib

PATH = "../data/oran-specs"

# Saved .html from https://specifications.o-ran.org/specifications
with open(f"{PATH}/O-RAN Downloads.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

work_groups = [wg.text for wg in soup.find_all("h3")]
all_documents = []

for table, wg in zip(soup.find_all("table", {"class": "table"}), work_groups):
    # First pass: get the doc names and download links
    documents = []
    for tr in table.find("tbody").find_all("tr"):
        for link in tr.find_all("a"):
            if not link.text:
                continue
            doc = link.parent.parent
            names = doc.find_all("span")
            
            documents.append({
                "name": names[0].text,
                "id": f"{names[1].text}",
                "link": link["href"]
            })
    
    # Second pass: get the doc descriptions
    descriptions = []
    for tr in table.find("tbody").find_all("tr"):
        for desc in tr.find_all("div", {"class": "col-11"}):
            paragraphs = [p.text for p in desc.find_all("p")]
            descriptions.append("\n".join(paragraphs))
    assert len(documents) == len(descriptions)

    # Third pass: consolidate
    for doc, desc in zip(documents, descriptions):
        doc["description"] = desc
        doc["work_group"] = wg
    all_documents.extend(documents)

for doc in all_documents:
    to = f"{PATH}/documents/"
    downloaded_path = wget.download(doc["link"], to)
    doc["filename"] = pathlib.Path(downloaded_path).name

with open(f"{PATH}/documents.json", "w", encoding="utf-8") as f:
    json.dump(all_documents, f, indent=2)
