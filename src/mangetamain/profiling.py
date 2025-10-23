import cProfile
import pstats

from mangetamain.streamlit_ui import main

if __name__ == "__main__":
    cProfile.run("main()", filename="docs/streamlit_profile.prof")
    stats = pstats.Stats("docs/streamlit_profile.prof")
    stats.strip_dirs().sort_stats("cumulative").print_stats(10)