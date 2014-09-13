import argparse
import os

import igraph
import pandas as pd


def process_dynamic_graph(filename, out_dir):

    g = igraph.Graph.Read_GraphML(filename)

    bcent = g.betweenness(weights='weight')
    evcent = g.eigenvector_centrality(weights='weight')
    deg = g.degree()

    this_index = [unicode(i, 'UTF-8') for i in g.vs['id']]

    df_bcent = pd.Series(bcent, index=this_index)
    df_evcent = pd.Series(evcent, index=this_index)
    df_deg = pd.Series(deg, index=this_index)

    filenames = {'betweenness.csv': df_bcent,
                 'ev_centrality.csv': df_evcent,
                 'degree.csv': df_deg}

    for fname, df in filenames.iteritems():
        try:
            os.mkdir(out_dir)
        except OSError:
            pass  # Ignore if directory already exists
        df.to_csv(os.path.join(out_dir, fname), encoding='UTF-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str,  help='GraphML input file')
    parser.add_argument('out_dir', type=str, help='Output directory')
    args = parser.parse_args()

    process_dynamic_graph(args.input_file, args.out_dir)


if __name__ == '__main__':
    main()
