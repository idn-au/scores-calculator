from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).parent
YAML_DIR = PROJECT_DIR.parent / "definitions"


def render_requirements(contents: list) -> str:
    render_str = "<table>"
    for req in contents:
        render_str += f"""<tr>
                <td>{req["description"]} [{req["value"]}]</td>"""
        if req.get("query"):
            render_str += f"""
                <td {'colspan="2"' if not req.get('conditions') else ''}><p>Query</p><pre>{req['query'].replace('<', '&lt;').replace('>', '&gt;')}</pre></td>"""
        if req.get("conditions"):
            render_str += f"""
            <td {'colspan="2"' if not req.get('query') else ''}><p>Conditions</p><ul>{''.join([f'<li>{cond["title"]}</li>' for cond in req['conditions']])}</ul></td>"""
        render_str += "</tr>"
    render_str += "</table>"
    return render_str


def render_scores(contents: dict) -> str:
    render_str = "<table>"
    for key, value in contents.items():
        render_str += f"""<tr>
            <td>
                <p>{key.upper() if key.upper() == value["title"] else f"{key.upper()} - {value['title']}"}</p>
                <p><em>{value["description"]}</em></p>
                {render_scores(value["scores"]) if value.get("scores") else render_requirements(value["requirements"])}
            </td>
        </tr>"""
    render_str += "</table>"
    return render_str


def main():
    render_str = ""
    for f in YAML_DIR.glob("*.yaml"):
        with open(f, "r") as file:
            contents = yaml.safe_load(file)
            render_str += f"<p>{f.stem.split('Def')[0].upper()}</p>"
            render_str += render_scores(contents)
    print(render_str)
    with open(PROJECT_DIR.parent / "test.html", "w") as f:
        f.write(render_str)


if __name__ == "__main__":
    main()
