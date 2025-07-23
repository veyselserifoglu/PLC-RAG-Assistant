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

def generate_markdown_output(all_data, ids_to_remove):
    """
    Generates a clean markdown file containing only document numbers and consolidated text.
    """
    markdown_lines = []

    # Add progress bar for markdown generation
    for i, data in tqdm(enumerate(all_data), desc="Generating markdown entries", unit="doc", total=len(all_data)):
        if (i + 1) in ids_to_remove:
            tqdm.write(f"Filtering out document: {i+1} ('{data.get('title', '')}')")
            continue
        
        markdown_lines.append(f"## Document {i+1}")
        
        # Consolidate all text content
        title = data.get('title', '')
        main_heading = data.get('main_heading', '')
        breadcrumbs = data.get('breadcrumbs', [])
        breadcrumbs_str = " ".join(breadcrumbs) if breadcrumbs else ""
        body_content = data.get('content', '')

        # Combine all text parts, ensuring they are not empty before joining.
        full_content_parts = [part for part in [title, main_heading, breadcrumbs_str, body_content] if part and part.strip()]
        merged_content = " ".join(full_content_parts)

        markdown_lines.append(merged_content)
        markdown_lines.append("")

    return "\n".join(markdown_lines)


def generate_metadata_output(all_data, ids_to_remove):
    """
    Generates a JSON file with metadata for each document.
    """
    metadata_list = []

    for i, data in tqdm(enumerate(all_data), desc="Generating metadata entries", unit="doc", total=len(all_data)):
        if (i + 1) in ids_to_remove:
            continue

        doc_metadata = {
            "document_number": i + 1,
            "source_link": data.get('source_link', ''),
            "canonical_url": data.get('canonical_url', ''),
            "title": data.get('title', ''),
            "main_heading": data.get('main_heading', ''),
            "breadcrumbs": data.get('breadcrumbs', [])
        }

        # Book metadata is now pre-extracted and attached to the data object
        book_info = {
            "book_title": data.get("book_title"),
            "edition": data.get("edition"),
            "publisher": data.get("publisher"),
            "publication_date": data.get("publication_date"),
        }
        # Add book info to metadata if it exists, filtering out keys with None values
        doc_metadata.update({k: v for k, v in book_info.items() if v})

        metadata_list.append(doc_metadata)

    return json.dumps(metadata_list, indent=4, ensure_ascii=False)


def extract_and_clean_book_metadata(content):
    """
    Extracts book metadata from a sentence at the end of the content
    and returns the metadata and the cleaned content.
    """
    # This regex is designed to find the specific sentence structure.
    book_info_pattern = re.compile(
        r"\s*(Speicherprogrammierbare Steuerungen.*?)\s+"
        r"(\d+\.\s*Auflage)\s+"
        r"erschienen im\s+(.*?)\s*,?\s*"
        r"(\d{4})\s*$"
    )

    book_metadata = {}
    cleaned_content = content
    
    match = book_info_pattern.search(content)
    
    if match:
        book_metadata = {
            "book_title": match.group(1).strip(),
            "edition": match.group(2).strip(),
            "publisher": match.group(3).strip(),
            "publication_date": match.group(4).strip(),
        }
        # Use re.sub for a safe replacement of the matched pattern
        cleaned_content = book_info_pattern.sub("", content).strip()
        
    return book_metadata, cleaned_content

def main(output_format: str = "markdown"):
    project_root = "."
    html_root_dir_abs = os.path.join(project_root, "www.seitz.et.hs-mannheim.de")
    output_content_file_abs = os.path.join(project_root, "cleaned_content.md")
    output_metadata_file_abs = os.path.join(project_root, "metadata.json")
    
    # Set a similarity threshold
    SIMILARITY_THRESHOLD = 0.95

    all_extracted_data = []
    seen_contents = set()
    processed_base_files = set()
    duplicate_count = 0
    similarity_duplicate_count = 0
    content_map = {}

    html_files = []
    for root, _, files in os.walk(html_root_dir_abs):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))

    # Use tqdm for progress bar
    for html_filepath_abs in tqdm(html_files, desc="Extracting content", unit="file"):
        base_name = os.path.basename(html_filepath_abs)
        is_no_cache_version = '@no_cache=1' in base_name
        
        # Skip no-cache versions if the base version has been processed
        if is_no_cache_version:
            original_file_name = base_name.split('@no_cache=1')[0]
            if original_file_name in processed_base_files:
                tqdm.write(f"Skipping no-cache version: {base_name}")
                continue
        
        data = extract_content_from_html(html_filepath_abs, project_root)
        if data and data['content']:
            content_hash = generate_content_hash(data['content'])
            if content_hash not in seen_contents:
                all_extracted_data.append(data)
                seen_contents.add(content_hash)
                content_map[content_hash] = data['content']
                duplicate_count += 1
            else:
                duplicate_count += 1
        
        if not is_no_cache_version:
            processed_base_files.add(base_name)

    # Second pass for similarity check
    unique_data = []
    seen_for_similarity = set()
    for data in tqdm(all_extracted_data, desc="Checking for similar content", unit="doc"):
        content_hash = generate_content_hash(data['content'])
        if content_hash in seen_for_similarity:
            continue

        is_similar = False
        for seen_hash in seen_for_similarity:
            similarity = calculate_text_similarity(content_map[content_hash], content_map[seen_hash])
            if similarity >= SIMILARITY_THRESHOLD:
                is_similar = True
                similarity_duplicate_count += 1
                tqdm.write(f"Found similar document (similarity: {similarity:.2f}). Skipping.")
                break
        
        if not is_similar:
            unique_data.append(data)
            seen_for_similarity.add(content_hash)

    all_extracted_data = unique_data
    total_duplicates = duplicate_count + similarity_duplicate_count
    print(f"\nProcessed files: {len(all_extracted_data) + total_duplicates}")
    print(f"Filtered out {duplicate_count} exact duplicates and {similarity_duplicate_count} similar documents (similarity >= {SIMILARITY_THRESHOLD}).")
    print(f"Total unique documents: {len(all_extracted_data)}")

    # New step: Extract book metadata and clean content in one pass
    for data in tqdm(all_extracted_data, desc="Extracting book metadata and cleaning content", unit="doc"):
        book_meta, cleaned_content = extract_and_clean_book_metadata(data['content'])
        data['content'] = cleaned_content
        if book_meta:
            data.update(book_meta)

    # IDs of documents to remove (1-based index)
    ids_to_remove = {
        # Content-related pages
        2,   # Beispielprogramme
        4,   # Wiederholungsfragen
        7,   # Sitemap
        10,
        11,  # Übungen
        43,  # Bibliotheken
        45,  # Videos
        292, # Apps zum Download
        293, # Funktionsbaustein-Bibliotheken
        294, # Funktionsbaustein-Bibliotheken
        295, # Funktionsbaustein-Bibliotheken
        # Boilerplate/Meta pages
        1,   # Anfahrt
        3,   # Datenschutzerklärung
        5,   # Erklärung zur Barrierefreiheit
        6,   # Impressum
        12   # Login
    }

    # The filtering logic has been moved into generate_markdown_output for efficiency.
    
    # Generate and save both files
    try:
        print("\nGenerating clean content file...")
        markdown_content = generate_markdown_output(all_extracted_data, ids_to_remove)
        print("Saving clean content file...")
        with open(output_content_file_abs, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        final_doc_count = markdown_content.count("## Document")
        print(f"Successfully saved {final_doc_count} documents to {output_content_file_abs}")

        print("\nGenerating metadata file...")
        metadata_content = generate_metadata_output(all_extracted_data, ids_to_remove)
        with open(output_metadata_file_abs, 'w', encoding='utf-8') as f:
            f.write(metadata_content)
        metadata_doc_count = len(json.loads(metadata_content))
        print(f"Successfully saved metadata for {metadata_doc_count} documents to {output_metadata_file_abs}")

    except Exception as e:
        print(f"An error occurred during file generation: {e}")


if __name__ == "__main__":
    main(output_format="markdown")