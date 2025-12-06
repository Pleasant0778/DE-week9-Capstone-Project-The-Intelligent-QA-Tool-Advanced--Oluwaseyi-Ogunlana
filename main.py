import argparse
from smart_qa.client import LLMClient

def main():
    parser = argparse.ArgumentParser(
        prog="smart_qa",
        description="Smart Q&A CLI Tool"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Load text from a file instead of pasting"
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save output to a file"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the persistent cache"
    )
    parser.add_argument(
        "--ask",
        nargs=2,
        metavar=("CONTEXT", "QUESTION"),
        help="Ask a question based on a context"
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Summarize the text"
    )
    parser.add_argument(
        "--extract-entities",
        action="store_true",
        help="Extract entities (People, Dates, Locations) from text"
    )

    args = parser.parse_args()
    client = LLMClient()

    # -------------------------
    # Clear cache if requested
    # -------------------------
    if args.clear_cache:
        client.clear_cache()

    # -------------------------
    # Load text from file if provided
    # -------------------------
    text = ""
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Failed to read file: {e}")
            return

    # -------------------------
    # Determine operation
    # -------------------------
    output = ""
    try:
        if args.summarize:
            if not text:
                print("Error: --summarize requires --file with text")
                return
            output = client.summarize(text)

        elif args.ask:
            context, question = args.ask
            output = client.ask(context, question)

        elif args.extract_entities:
            if not text:
                print("Error: --extract-entities requires --file with text")
                return
            output = client.extract_entities(text)

        else:
            parser.print_help()
            return

    except Exception as e:
        print(f"Error: {e}")
        return

    # -------------------------
    # Print output
    # -------------------------
    print("\n=== OUTPUT ===")
    print(output)

    # -------------------------
    # Save output if requested
    # -------------------------
    if args.save:
        try:
            with open(args.save, "w", encoding="utf-8") as f:
                f.write(str(output))
            print(f"\nOutput saved to {args.save}")
        except Exception as e:
            print(f"Failed to save output: {e}")


if __name__ == "__main__":
    main()
