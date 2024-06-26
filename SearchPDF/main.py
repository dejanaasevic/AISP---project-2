import os
import re
from difflib import get_close_matches
import fitz

from SearchPDF.Trie import Trie
from SearchPDF.page_graph import PageGraph
from SearchPDF.pdf_parse import *
from SearchPDF.search import search_document
from SearchPDF.serialization import *

pdf_file_path = '../data/Data Structures and Algorithms in Python.pdf'
output_file_path = '../data/parsed_text.txt'
trie_file_path = '../data/trie_data.pkl'
graph_file_path = '../data/page_graph.pkl'
output_pdf_path = '../data/search_results.pdf'


def build_trie_and_graph(document_text):
    print("Building Trie and Graph")
    trie = Trie()
    graph = PageGraph()
    page_reference_pattern = re.compile(r'\bpage (\d+)\b', re.IGNORECASE)
    section_reference_pattern = re.compile(r'\bsee section (\d+\.\d+(?:\.\d+)*)\b', re.IGNORECASE)

    pages = document_text.split('--- Page ')[1:]
    section_to_page = {}
    current_section = None

    for index, page_text in enumerate(pages):
        page_number = index + 1
        print(f"Processing page {page_number}")

        words = page_text.split()
        for word in words:
            trie.insert(word.lower())

        for match in page_reference_pattern.findall(page_text):
            target_page = int(match)
            graph.add_reference(page_number, target_page)

        for match in section_reference_pattern.findall(page_text):
            if match in section_to_page:
                target_page = section_to_page[match]
                graph.add_reference(page_number, target_page)

        section_match = re.search(r'\bsection (\d+\.\d+(?:\.\d+)*)\b', page_text, re.IGNORECASE)
        if section_match:
            current_section = section_match.group(1)
            section_to_page[current_section] = page_number

    print("Trie and Graph building completed")
    return trie, graph


def display_menu():
    print("\nPDF Document Search")
    print("1. Pretraga pojma")
    print("2. Izlaz")
    choice = input("Izaberite opciju: ")
    return choice


def paginate_results(results, page_size=10):
    pages = []
    for i in range(0, len(results), page_size):
        pages.append(results[i:i + page_size])
    return pages


def suggest_alternatives(query, document_text):
    words = set(re.findall(r'\w+', document_text.lower()))
    suggestions = get_close_matches(query.lower(), words, n=3, cutoff=0.7)
    return suggestions


def autocomplete(trie, prefix):
    node = trie.root
    for char in prefix:
        if char not in node.children:
            return []
        node = node.children[char]
    return dfs(node, prefix, count=3)


def dfs(node, current_prefix, count):
    suggestions = []
    if node.word_end:
        suggestions.append(current_prefix)
    for char, child in node.children.items():
        if len(suggestions) >= count:
            break
        suggestions.extend(dfs(child, current_prefix + char, count))
    return suggestions[:count]


def save_search_results_as_pdf(results, original_pdf_path, output_pdf_path, max_results=10):
    doc = fitz.open(original_pdf_path)
    writer = fitz.open()
    pages_to_include = set()
    for result in results[:max_results]:
        page_number = result[0] - 1
        if 0 <= page_number < len(doc):
            pages_to_include.add(page_number)
    for page_number in sorted(pages_to_include):
        writer.insert_pdf(doc, from_page=page_number, to_page=page_number)
    writer.save(output_pdf_path)
    print(f"Search results saved to {output_pdf_path}")


def main():
    trie = load_trie(trie_file_path)
    graph = load_graph(graph_file_path)
    if trie is None or graph is None:
        if not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0:
            parse_pdf_to_text(pdf_file_path, output_file_path)
        document_text = load_parsed_text(output_file_path)
        trie, graph = build_trie_and_graph(document_text)
        save_trie(trie, trie_file_path)
        save_graph(graph, graph_file_path)
    else:
        document_text = load_parsed_text(output_file_path)
    while True:
        choice = display_menu()
        if choice == '1':
            query = input("Unesite pojam za pretragu: ").strip()
            search_results = None
            if "*" in query:
                prefix = query.replace("*", "")
                autocomplete_suggestions = autocomplete(trie, prefix)
                if autocomplete_suggestions:
                    print("Predlozi za autocomplete:")
                    for suggestion in autocomplete_suggestions:
                        print(f"- {suggestion}")
                    selected_autocomplete_suggestion = input(
                        "Izaberite sugestiju za pretragu (ili pritisnite Enter za izlaz): ").strip()
                    if selected_autocomplete_suggestion and selected_autocomplete_suggestion in autocomplete_suggestions:
                        search_results = search_document(trie, graph, document_text, selected_autocomplete_suggestion)
                    else:
                        print("Izlaz iz programa.")
                        continue
            if not search_results:
                search_results = search_document(trie, graph, document_text, query)
            if not search_results:
                print("Nema rezultata za prikaz.")
                suggestions = suggest_alternatives(query, document_text)
                if suggestions:
                    print("Mislili ste na:")
                    for suggestion in suggestions:
                        print(f"- {suggestion}")
                    selected_suggestion = input(
                        "Izaberite sugestiju za pretragu (ili pritisnite Enter za izlaz): ").strip()
                    if selected_suggestion and selected_suggestion in suggestions:
                        search_results = search_document(trie, graph, document_text, selected_suggestion)
                    else:
                        print("Izlaz iz programa.")
                        continue
            if search_results:
                result_number = 0
                pages = paginate_results(search_results, page_size=10)
                current_page = 0
                while True:
                    if current_page < len(pages):
                        for result in pages[current_page]:
                            page = result[0]
                            contexts = result[1]
                            total_score = result[2]
                            result_number += 1
                            print(f"Rezultat {result_number}")
                            print(f"Ukupan broj bodova: {total_score}")
                            print(f"Stranica: {page}")
                            print("Kontekst:")
                            for context in contexts:
                                print(f"- {context}")
                            print()
                        if current_page < len(pages) - 1:
                            next_page = input("Prikaz sledeće strane? (da/ne): ")
                            if next_page.lower() == 'da':
                                current_page += 1
                            else:
                                break
                        else:
                            print("Nema više rezultata.")
                            break
                    else:
                        print("Nema više rezultata.")
                        break
                save_search_results_as_pdf(search_results, pdf_file_path, output_pdf_path)
        elif choice == '2':
            print("Izlaz iz programa.")
            break
        else:
            print("Nevažeća opcija. Molimo pokušajte ponovo.")


if __name__ == "__main__":
    main()
