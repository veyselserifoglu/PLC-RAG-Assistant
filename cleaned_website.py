import os
import json
import re
import hashlib
import difflib
from collections import defaultdict
from bs4 import BeautifulSoup
from tqdm import tqdm

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

def generate_content_hash(content):
    """
    Generate a stable hash for content to detect duplicates.
    This is more reliable than Python's built-in hash() which is randomized between sessions.
    """
    # Normalize the content by lowercasing and stripping excessive whitespace
    normalized = re.sub(r'\s+', ' ', content.lower()).strip()
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def calculate_text_similarity(text1, text2):
    """
    Calculate similarity between two text strings using difflib's SequenceMatcher.
    Returns a float between 0 and 1, where 1 means identical.
    """
    # Normalize the texts (lowercase and remove extra whitespace)
    text1 = re.sub(r'\s+', ' ', text1.lower()).strip()
    text2 = re.sub(r'\s+', ' ', text2.lower()).strip()
    
    # Use SequenceMatcher to calculate similarity ratio
    similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
    return similarity

def generate_markdown_output(all_data):
    """
    Generates a single Markdown string from all extracted data in the specified format.
    """
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")

    markdown_lines = ["# Documents Collection", ""]
    markdown_lines.append("---")
    markdown_lines.append("")

    # Add progress bar for markdown generation
    for i, data in tqdm(enumerate(all_data), desc="Generating markdown entries", unit="doc", total=len(all_data)):
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
    project_root = "/home/veysel/dev-projects/PLC-RAG-Assistant"
    html_root_dir_abs = os.path.join(project_root, "www.seitz.et.hs-mannheim.de")

    output_json_file_abs = os.path.join(project_root, "extracted_content_v2.json")
    output_markdown_file_abs = os.path.join(project_root, "extracted_content_v2.md")
    
    all_extracted_data = []
    # Track content hashes for exact duplicates
    seen_contents = set()
    # Store content for similarity checks - mapping hash to actual content
    content_store = {}
    # Set similarity threshold
    SIMILARITY_THRESHOLD = 0.97
    # Track duplicate counts
    duplicate_count = 0
    similarity_duplicate_count = 0

    print(f"Starting scan in directory: {html_root_dir_abs}")

    # First collect all HTML files to process
    all_html_files = []
    for dirpath, _, filenames in os.walk(html_root_dir_abs):
        filenames.sort()
        for filename in filenames:
            if filename.endswith(".html"):
                all_html_files.append((dirpath, filename))
    
    print(f"Found {len(all_html_files)} HTML files to process")
    
    processed_base_files = set()
    
    # Process files with a progress bar
    for dirpath, filename in tqdm(all_html_files, desc="Processing HTML files", unit="file"):
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
                if os.path.exists(base_file_path_abs) and base_name != filename: # ensure it's not comparing to itself
                    # Using tqdm.write to not interfere with progress bar
                    tqdm.write(f"Skipping no_cache version {html_filepath_abs} as base file {base_file_path_abs} exists.")
                    continue
            
            # Using tqdm.write for clean output with progress bar
            tqdm.write(f"Processing: {html_filepath_abs}")
            extracted_data = extract_content_from_html(html_filepath_abs, project_root)
            
            if extracted_data:
                # Get the content and generate a hash for duplicate detection
                content = extracted_data.get('content', '')
                
                # Skip very short content as it might be error pages
                if len(content) < 20:  # Arbitrary threshold for minimal meaningful content
                    tqdm.write(f"Skipping {html_filepath_abs} due to insufficient content length.")
                    continue
                    
                # Generate content hash using our helper function
                content_hash = generate_content_hash(content)
                
                # Check if we've already seen this exact content
                if content_hash in seen_contents:
                    duplicate_count += 1
                    tqdm.write(f"Exact duplicate content detected in {html_filepath_abs}. Skipping.")
                    continue
                
                # Check for similar content
                is_similar = False
                # Display progress for similarity checking if many documents
                similarity_iter = content_store.items()
                if len(content_store) > 10:  # Only show nested progress for larger document sets
                    similarity_iter = tqdm(similarity_iter, desc="Checking document similarity", 
                                          leave=False, unit="doc", total=len(content_store))
                
                for existing_hash, existing_content in similarity_iter:
                    similarity = calculate_text_similarity(content, existing_content)
                    if similarity >= SIMILARITY_THRESHOLD:
                        similarity_duplicate_count += 1
                        tqdm.write(f"Similar content detected in {html_filepath_abs} (similarity: {similarity:.4f}). Skipping.")
                        is_similar = True
                        break
                
                if not is_similar:
                    # Add to tracking set, content store, and save the data
                    seen_contents.add(content_hash)
                    content_store[content_hash] = content
                    all_extracted_data.append(extracted_data)
                
            if not is_no_cache_version:
                processed_base_files.add(base_name)


    total_duplicates = duplicate_count + similarity_duplicate_count
    print(f"\nProcessed files: {len(all_extracted_data) + total_duplicates}")
    print(f"Filtered out {duplicate_count} exact duplicates and {similarity_duplicate_count} similar documents (similarity >= {SIMILARITY_THRESHOLD}).")
    print(f"Total unique documents: {len(all_extracted_data)}")
    
    if output_format == "json":
        try:
            print("Saving JSON output...")
            with open(output_json_file_abs, 'w', encoding='utf-8') as f:
                json.dump(all_extracted_data, f, ensure_ascii=False, indent=4)
            print(f"Successfully saved {len(all_extracted_data)} unique documents to {output_json_file_abs}")
        except Exception as e:
            print(f"Error saving JSON to file {output_json_file_abs}: {e}")
    elif output_format == "markdown":
        try:
            print("Generating Markdown output...")
            markdown_content = generate_markdown_output(all_extracted_data)
            print("Saving Markdown file...")
            with open(output_markdown_file_abs, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Successfully saved {len(all_extracted_data)} unique documents to {output_markdown_file_abs}")
        except Exception as e:
            print(f"Error saving Markdown to file {output_markdown_file_abs}: {e}")
    else:
        print(f"Unknown output format: {output_format}. Please choose 'json' or 'markdown'.")

if __name__ == "__main__":
    main()