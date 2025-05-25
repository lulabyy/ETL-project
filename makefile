etl:
	python main_etl.py

streamlit:
	streamlit run main_streamlit.py

all:
	make etl
	make streamlit
