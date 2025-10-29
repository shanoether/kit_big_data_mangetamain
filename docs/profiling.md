# Profiling Guide
This guide explains how to profile the performance of your Streamlit application using two different methods:

- cProfile — for generating detailed profiling reports and visualizing them with Snakeviz

- py-spy — for real-time profiling or for generating an interactive flamegraph in SVG format

## 1️⃣ Profiling using cProfile

🔧 How to run

1. Run the Streamlit app with profiling enabled:

    ```bash
    streamlit run src/mangetamain/streamlit_ui.py profile
    ```

2. Interact with your app as usual — all function calls and timings will be recorded.

3. After you finish testing, stop the app and visualize the profile using Snakeviz:

    ```bash
    snakeviz docs/streamlit_profile.prof
    ```

4. Open the visualization in your browser: [link](http://127.0.0.1:8080/snakeviz/streamlit_profile.prof)


## 2️⃣ Profiling in realtime

🔧 How to run

1. Start your Streamlit application:

    ```bash
    streamlit run src/mangetamain/streamlit_ui.py
    ```

2. Find the process ID (PID) of the running Streamlit process:

    ```bash
    ps aux | grep "[s]treamlit run src/mangetamain/streamlit_ui.py" | awk '{print $2}'
    ```

3. To view real-time profiling in a new terminal:

    ```bash
    py-spy top --pid <PID>
    ```

4. To record and visualize the performance data:

    ```bash
    py-spy record -o profile.svg --pid <PID>
    ```

5. If you encounter permission errors (e.g., when accessing another user’s process), use:

    ```bash
    sudo env "PATH=$PATH" py-spy top --pid <PID>
    sudo env "PATH=$PATH" py-spy record -o docs/streamlit_profile.svg --pid <PID>
    ```

6. Interact with the app while profiling, then stop the process when finished. You can then open streamlit_profile.svg in your browser to explore the flamegraph.
