from graphs import generate_planner_graph,evaluate_level_test_graph

def graph_to_image(compiled_graph, output_file="graph.png"):
    png_bytes = compiled_graph.get_graph().draw_mermaid_png()
    with open(output_file, "wb") as f:
        f.write(png_bytes)
    print(f"Graph image saved as {output_file}")

if __name__ == "__main__": 
    compile_graph = evaluate_level_test_graph()
    # graph_to_image(compile_graph, "planner.png")
    graph_to_image(compile_graph, "eval.png")