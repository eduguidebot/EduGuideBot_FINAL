# scripts/build_web_apps.py
import json
import os
import shutil

def inject_data_into_template(data: list, template_path: str, output_path: str):
    """A reusable function to inject JSON data into an HTML template."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        json_string = json.dumps(data, ensure_ascii=False)
        # This creates a JavaScript variable `universityData` inside the HTML
        data_injection_script = f"const universityData = {json_string};"
        
        final_html = template_content.replace('// %%UNIVERSITY_DATA%%', data_injection_script)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"✅ Successfully built: {os.path.basename(output_path)}")

    except Exception as e:
        print(f"❌ ERROR building {os.path.basename(output_path)}: {e}")

def main():
    """Builds all data-driven Web Apps for the project."""
    print("--- Starting Web App Build Process ---")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_root, 'data', 'data.json')

    # Load master data once
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            universities = json.load(f)
        print(f"Loaded {len(universities)} universities from data.json.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Could not read master data file at {data_path}. Error: {e}")
        return

    # --- Define Web Apps to Build ---
    # We must ensure the template files exist first.
    # We assume the AI has created them. If not, this script will fail gracefully.
    
    apps_to_build = [
        {"name": "University Catalog", "template": os.path.join(project_root, 'static', 'browser', 'index.template.html'), "output": os.path.join(project_root, 'static', 'browser', 'index.html')},
        {"name": "Cost Calculator", "template": os.path.join(project_root, 'static', 'calculator', 'index.template.html'), "output": os.path.join(project_root, 'static', 'calculator', 'index.html')},
        {"name": "Student DNA Quiz", "template": os.path.join(project_root, 'static', 'quiz', 'index.template.html'), "output": os.path.join(project_root, 'static', 'quiz', 'index.html')}
    ]

    for app in apps_to_build:
        if os.path.exists(app['template']):
            print(f"\nBuilding {app['name']}...")
            inject_data_into_template(universities, app['template'], app['output'])
        else:
            print(f"\n⚠️ WARNING: Template file not found, skipping build for {app['name']}: {app['template']}")
    
    print("\n--- Build Process Finished ---")

if __name__ == '__main__':
    main()