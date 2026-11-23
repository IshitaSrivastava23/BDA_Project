import fitz
import json

doc = fitz.open("Healthcare_BigData_Analytics_Assignment.pdf")
pages_data = []

for i, page in enumerate(doc):
    p_info = {
        "page_number": i + 1,
        "width": page.rect.width,
        "height": page.rect.height,
        "blocks": []
    }
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if b.get("type") == 0: # text block
            b_info = {
                "bbox": [round(x, 1) for x in b["bbox"]],
                "lines": []
            }
            for l in b["lines"]:
                line_text = "".join([s["text"] for s in l["spans"]]).strip()
                s0 = l["spans"][0]
                b_info["lines"].append({
                    "text": line_text,
                    "font": s0["font"],
                    "size": round(s0["size"], 1),
                    "flags": s0["flags"],
                    "color": s0["color"],
                    "bbox": [round(x, 1) for x in l["bbox"]]
                })
            p_info["blocks"].append(b_info)
    pages_data.append(p_info)

with open("reference_structure.json", "w", encoding="utf-8") as f:
    json.dump(pages_data, f, indent=2)

print("Saved reference_structure.json with 15 pages data.")
