test : 
	python -m unittest -vb tests

clean : 
	rm -f *.pyc */*.pyc

clobber : clean
	rm -f *.db

# eof
