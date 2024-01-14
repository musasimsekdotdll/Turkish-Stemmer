# CMPE492: DEVELOPING A TURKISH STEMMER

## How to run
1. Clone this repository:

   ```
   git clone https://github.com/musasimsekdotdll/Turkish-Stemmer.git
   ```

2. Install requirements using pipenv:

    ```
    pipenv install
    ```

	If you do not have pipenv in your environment, follow [this link](https://pypi.org/project/pipenv/).

3. Import the search function in a Python script:	

    ```
    from trie import searchStem
    ```

4. Call the function with a word and see the results:
	
    ```
    result = searchStem('gözlemlediklerimizdekiysen')
    ```

## How to test the Stemmer

1. Follow instructions to install Morphological Analyzer: https://github.com/BOUN-TABILab-TULAP/Morphological-Parser

2. Go to ***testing*** directory in this project.

3. Run the testing script to see the results:
	
    ```
    pipenv run python test_stemmer.py
    ```
