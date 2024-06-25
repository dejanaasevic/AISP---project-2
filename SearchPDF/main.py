import os
import re
from SearchPDF.Trie import Trie
from SearchPDF.page_graph import PageGraph
from SearchPDF.pdf_parse import parse_pdf_to_text, load_parsed_text
from SearchPDF.search import search_document
from SearchPDF.serialization import load_trie, save_trie, load_graph, save_graph

pdf_file_path = '../data/Data Structures and Algorithms in Python.pdf'
output_file_path = '../data/parsed_text.txt'
trie_file_path = '../data/trie_data.pkl'
graph_file_path = '../data/page_graph.pkl'


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
            query = input("Unesite pojam za pretragu: ")
            # autocomplete_suggestions = autocomplete(trie, query)
            # if autocomplete_suggestions:
            #    print("Predlozi za autocomplete:")
            #    for suggestion in autocomplete_suggestions:
            #        print(f"- {suggestion}")

            search_results = search_document(trie, graph, document_text, query)
            if not search_results:
                print("Nema rezultata za prikaz.")
            # suggestions = suggest_alternatives(query, document_text)
            # if suggestions:
            #     print("Mislili ste na:")
            #    for suggestion in suggestions:
            #       print(f"- {suggestion}")
            else:
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
                            next_page = input("Prikaz sledeće strane? (d/n): ")
                            if next_page.lower() == 'd':
                                current_page += 1
                            else:
                                break
                        else:
                            print("Nema više rezultata.")
                            break
                    else:
                        break
        elif choice == '2':
            print("Izlaz iz programa.")
            break
        else:
            print("Nevažeća opcija. Pokušajte ponovo.")


if __name__ == "__main__":
    main()
