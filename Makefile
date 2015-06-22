all:
	./SimpleServer.py

test:
	./airlineTSP.py

clean:
	-rm gurobi.log *.pyc *.lp
