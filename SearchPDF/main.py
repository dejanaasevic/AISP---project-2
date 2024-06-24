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
    trie = Trie()
    graph = PageGraph()
    page_reference_pattern = re.compile(r'\bpage (\d+)\b', re.IGNORECASE)
    section_reference_pattern = re.compile(r'\bsee section (\d+\.\d+(?:\.\d+)*)\b', re.IGNORECASE)

    pages = document_text.split('--- Page ')[1:]
    section_to_page = {}
    current_section = None

    for index, page_text in enumerate(pages):
        page_number = index + 1

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

    return trie, graph


def display_menu():
    print("\nPDF Document Search")
    print("1. Pretraga pojma")
    print("2. Izlaz")
    choice = input("Izaberite opciju: ")
    return choice


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
            search_results = search_document(trie, graph, document_text, query)
            if not search_results:
                print("Nema rezultata za prikaz.")
            else:
                print()
                print(f"Pronađeno {len(search_results)} stranica sa pojmom '{query}':")
                result_index = 1
                for page, contexts, _ in search_results:
                    for context in contexts:
                        print(f"Rezultat {result_index}:")
                        print(f"Stranica: {page}, Kontekst: {context}\n")
                        result_index += 1
        elif choice == '2':
            print("Izlaz iz programa.")
            break
        else:
            print("Nevažeća opcija. Pokušajte ponovo.")


if __name__ == "__main__":
    main()