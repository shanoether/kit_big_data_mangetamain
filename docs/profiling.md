# Profiling Guide

## How to use

### Profiling using cProfile

- run

    ```bash
    streamlit run src/mangetamain/profiling.py
    ```

- after starting application, test the web as you wish and stop after finish

- visualize 

    ```bash
    snakeviz docs/streamlit_profile.prof
    ```

- open the visualization using this [link](http://127.0.0.1:8080/snakeviz/streamlit_profile.prof)


### Profiling in realtime

- run the application first
    ```bash
    streamlit run src/mangetamain/streamlit_ui.py
    ```

- find the pid of the running process

    ```bash
    ps aux | grep "[s]treamlit run src/mangetamain/streamlit_ui.py" | awk '{print $2}'
    ```

- if want to run realtime profiling 

    ```bash
    py-spy top --pid <PID>
    ```

- if want to save and visualize instead

    ```bash
    py-spy record -o profile.svg --pid <PID>
    ```

- add sudo env "PATH=$PATH" if has errors:

    ```bash
    sudo env "PATH=$PATH" py-spy top --pid <PID>
    sudo env "PATH=$PATH" py-spy record -o docs/streamlit_profile.svg --pid <PID>
    ```

- test the application before quitting

- the result of visualization will be saved to streamlit_profile.svg
