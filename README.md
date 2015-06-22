# Edge Cover
An example of using Gurobi to compute a minimal edge cover

![](screenshot2.png?raw=true)

# Running the example

1. Start Python's webserver from the command line
    ```
    make
    ```

2. Point your browser at http://localhost:8000

3. Add some nodes with by clicking your mouse in the demo area.

4. Click "Compute Edge Cover" to find the minimal edge cover.

# Performing an optimization

To just solve the edge cover model (without running a web server) do:

```
make test
```

## Sources

The [d3][3] code for this example is based on Mike Bostock's ["Build your own Graph"][1] [block][2].

[1]: http://bl.ocks.org/mbostock/929623
[2]: http://bl.ocks.org/mbostock
[3]: http://d3js.org