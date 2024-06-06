## Setup Instructions

Before running the project, it's necessary to set up a virtual environment with the required dependencies. Follow the steps below to create the virtual environment and install the necessary libraries: **Dockefile will be provided soon for easy environment setup**

1.  **Create Virtual Environment:** Open your terminal or command prompt and navigate to the project directory.

    ```bash
    python -m venv venv
    ```

    This command will create a virtual environment named `venv` in your project directory.

2.  **Activate Virtual Environment:** Activate the virtual environment.

    - **On Windows:**

      ```bash
      venv\Scripts\activate
      ```

    - **On macOS and Linux:**
      ```bash
      source venv/bin/activate
      ```

3.  **Install Dependencies:** Once the virtual environment is activated, install the required libraries using pip.

    ```bash
    pip install -r AI/model_loading/requirements.txt
    ```

    The `requirements.txt` file is located in the `model_loading` folder under the `AI` directory.

4.  **Run Notebook:** After installing the dependencies, you can run the project notebook locally.

    ```bash
    jupyter notebook Translation.ipynb
    ```

    Replace `Translation.ipynb` with the actual name of your notebook file.

5.  **Alternatively, Run Notebook in Google Colab:** You can also run the project notebook in Google Colab. After running the notebook and generating the `.pkl` file, download it and copy it into the project directory.

        - Open the notebook in Google Colab.
        - Run the notebook cells.
        - After generating the `.pkl` file, download it.
        - Copy the downloaded `.pkl` file into the project directory.

6.  **Inside the function: translate_from_french_to_english** - Replace with the path of the downladed .pkl model
