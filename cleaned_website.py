import os
import json
import re
from bs4 import BeautifulSoup

def extract_content_from_html(html_filepath_abs, project_root_dir):
    """
    Extracts title, cleaned text content, and source link from an HTML file.
    """
    try:
        with open(html_filepath_abs, 'r', encoding='utf-8') as f:
            html_string = f.read()

        soup = BeautifulSoup(html_string, 'html.parser')

        # Extract title
        page_title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"

        # Extract Canonical URL
        canonical_url_tag = soup.find('link', rel='canonical')
        canonical_url = canonical_url_tag['href'].strip() if canonical_url_tag and canonical_url_tag.has_attr('href') else ""

        # Extract Breadcrumbs from JSON-LD
        breadcrumbs_list = []
        script_ld_json = soup.find('script', type='application/ld+json')
        if script_ld_json and script_ld_json.string:
            try:
                json_data = json.loads(script_ld_json.string)
                # Handle case where json_data is a list of schemas or a single schema
                schemas = json_data if isinstance(json_data, list) else [json_data]
                for schema in schemas:
                    if schema.get('@type') == 'BreadcrumbList' and 'itemListElement' in schema:
                        for item in schema['itemListElement']:
                            if item.get('@type') == 'ListItem' and 'item' in item and 'name' in item['item']:
                                breadcrumbs_list.append(item['item']['name'].strip())
                        break # Found BreadcrumbList
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON-LD in {html_filepath_abs}")

        # Attempt to extract content using TYPO3SEARCH comments
        typo3_search_content = None
        # Use a non-greedy match for content between the comments
        match = re.search(r'<!--TYPO3SEARCH_begin-->(.*?)<!--TYPO3SEARCH_end-->', html_string, re.DOTALL | re.IGNORECASE)
        if match:
            content_html_str = match.group(1)
            content_soup = BeautifulSoup(content_html_str, 'html.parser')
            typo3_search_content = content_soup

        main_content_element = None
        if typo3_search_content:
            main_content_element = typo3_search_content
        else:
            # Fallback to <main class="c-page__content">
            main_content_tag = soup.find('main', class_='c-page__content')
            if main_content_tag:
                main_content_element = main_content_tag
            else:
                # Fallback to the whole body if no specific main content found
                # This is less ideal as it might include headers/footers if not careful
                # but TYPO3SEARCH or main.c-page__content should be the primary targets
                print(f"Warning: Neither TYPO3SEARCH comments nor <main class='c-page__content'> found in {html_filepath_abs}. Considering body.")
                main_content_element = soup.body # Or None, if we want to be stricter

        cleaned_text = "No main content extracted"
        main_heading = ""

        if main_content_element:
            # Extract Main Heading (H1) from the main content element
            h1_tag = main_content_element.find('h1')
            if h1_tag and h1_tag.string:
                main_heading = h1_tag.string.strip()
            elif h1_tag and h1_tag.get_text(strip=True): # Handle cases where H1 might contain other tags
                main_heading = h1_tag.get_text(separator=' ', strip=True)

            # Remove script and style tags from the extracted main content
            for script_or_style in main_content_element.find_all(['script', 'style']):
                script_or_style.decompose()
            
            # Get text, separating by space, and stripping leading/trailing whitespace from lines
            cleaned_text = main_content_element.get_text(separator=' ', strip=True)
        
        # Create a source link relative to the project_root_dir
        source_link = os.path.relpath(html_filepath_abs, project_root_dir)

        return {
            "title": page_title,
            "main_heading": main_heading,
            "content": cleaned_text,
            "source_link": source_link.replace(os.sep, '/'), # Ensure forward slashes for consistency
            "canonical_url": canonical_url,
            "breadcrumbs": breadcrumbs_list
        }

    except Exception as e:
        print(f"Error processing file {html_filepath_abs}: {e}")
        return None

def generate_markdown_output(all_data):
    """
    Generates a single Markdown string from all extracted data in the specified format.
    """
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")

    markdown_lines = ["# Documents Collection", ""]
    markdown_lines.append("---")
    markdown_lines.append("")

    for i, data in enumerate(all_data):
        markdown_lines.append(f"## Document {i+1}")
        markdown_lines.append("")
        markdown_lines.append("**Title:**  ")
        markdown_lines.append(data.get('title', 'N/A'))
        markdown_lines.append("")
        markdown_lines.append(f"**Source Link:** {data.get('source_link', 'N/A')}")
        markdown_lines.append(f"**Main Heading:** {data.get('main_heading', 'N/A')}")
        
        breadcrumbs = data.get('breadcrumbs', [])
        breadcrumbs_str = ", ".join(breadcrumbs) if breadcrumbs else "N/A"
        markdown_lines.append(f"**Breadcrumbs:** {breadcrumbs_str}")
        
        markdown_lines.append(f"**Canonical URL:** {data.get('canonical_url', 'N/A')}")
        markdown_lines.append("")
        markdown_lines.append("**Body Content:**  ")
        markdown_lines.append(data.get('content', 'No content extracted'))
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")

    return "\n".join(markdown_lines)

def main(output_format: str = "markdown"):
    project_root = "/home/dev/dev-projects/PLC-RAG-Assistant"
    html_root_dir_abs = os.path.join(project_root, "www.seitz.et.hs-mannheim.de")

    output_json_file_abs = os.path.join(project_root, "extracted_content.json")
    output_markdown_file_abs = os.path.join(project_root, "extracted_content.md")
    
    all_extracted_data = []

    print(f"Starting scan in directory: {html_root_dir_abs}")

    for dirpath, _, filenames in os.walk(html_root_dir_abs):
        filenames.sort()
        
        processed_base_files = set()

        for filename in filenames:
            if filename.endswith(".html"):
                base_name = filename
                is_no_cache_version = False

                if filename.endswith("@no_cache=1.html"):
                    base_name = filename.replace("@no_cache=1.html", ".html")
                    is_no_cache_version = True
                
                html_filepath_abs = os.path.join(dirpath, filename)

                # Skip @no_cache=1.html if the base file exists or has been processed
                if is_no_cache_version:
                    base_file_path_abs = os.path.join(dirpath, base_name)
                    if os.path.exists(base_file_path_abs) and base_name != filename : # ensure it's not comparing to itself
                        print(f"Skipping no_cache version {html_filepath_abs} as base file {base_file_path_abs} exists.")
                        continue
                
                print(f"Processing: {html_filepath_abs}")
                extracted_data = extract_content_from_html(html_filepath_abs, project_root)
                if extracted_data:
                    all_extracted_data.append(extracted_data)
                
                if not is_no_cache_version:
                    processed_base_files.add(base_name)


    print(f"\nProcessed {len(all_extracted_data)} HTML files.")
    
    if output_format == "json":
        try:
            with open(output_json_file_abs, 'w', encoding='utf-8') as f:
                json.dump(all_extracted_data, f, ensure_ascii=False, indent=4)
            print(f"Successfully saved extracted data to {output_json_file_abs}")
        except Exception as e:
            print(f"Error saving JSON to file {output_json_file_abs}: {e}")
    elif output_format == "markdown":
        try:
            markdown_content = generate_markdown_output(all_extracted_data)
            with open(output_markdown_file_abs, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Successfully saved extracted data to {output_markdown_file_abs}")
        except Exception as e:
            print(f"Error saving Markdown to file {output_markdown_file_abs}: {e}")
    else:
        print(f"Unknown output format: {output_format}. Please choose 'json' or 'markdown'.")

if __name__ == "__main__":
    main()