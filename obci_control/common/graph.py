#!/usr/bin/python
# -*- coding: utf-8 -*-


class Graph(object):

    def __init__(self, bidirectional=False):

        self._edges = []
        self._nlist = {}
        self._bidir = bidirectional

    def copy(self):
        gr = Graph(self._bidir)
        # print "bef copy: ", self.vertices()
        # print "edges_bef:  ", self._edges
        copied = {}
        for (v1,v2) in self._edges:

            for v in (v1, v2):
                if v._model not in copied:
                    copied[v._model] = v.copy(gr)
                
            cv1 = copied[v1._model]
            cv2 = copied[v2._model]
            gr.add_edge(cv1, cv2)

        for v in self._nlist:
            if self._nlist[v] == [] and not v.in_edges():
                gr.add_vertex(v.copy(gr))

        # print "copied: ", gr.vertices()
        # print "edges copied:  ", gr._edges
        return gr

    def is_bidirectional(self):
        return False

    def vertices(self):
        return self._nlist.keys()

    def _edges_(self):
        return self._edges

    def _neighbours(self, vertex):
        return self._nlist[vertex]

    def add_vertex(self, vertex):
        if vertex not in self._nlist:
            self._nlist[vertex] = []

    def add_edge(self, v_a, v_z):
        for v in [v_a, v_z]:
            if v not in self._nlist:
                self._nlist[v] = []
        
        if not v_z in self._nlist[v_a]:
            self._nlist[v_a].append(v_z)
            self._edges.append((v_a, v_z))

    def remove_edge(self, edge):
        v_a, v_z = edge
        if (v_a, v_z) in self._edges:
            self._edges.remove((v_a, v_z))
            self._nlist[v_a].remove(v_z)
        else:
            raise Exception("edge not in graph")

    def remove_vertex(self, vertex):
        if vertex not in self._nlist:
            raise Exception("vertex not in graph")
        
        ins = vertex.in_edges()
        outs = vertex.out_edges()

        for e in ins + outs:
            self.remove_edge(e)
        del self._nlist[vertex]

    def topo_sort(self):
        # print "****************************"

        gr = self.copy()
        vertices = gr.vertices()
        result = []
        len_res = 0

        cycle = False
        while not len_res == len(vertices):
            sinks = [v for v in gr.vertices() if not v.out_edges()]
            # print 'sinks: ', sinks
            if not sinks:
                print 'cycle :('
                cycle = True
                break

            result.append(sinks)
            # print "now:",result
            len_res += len(sinks)

            for s in sinks:
                for ine in s.in_edges():
                    gr.remove_edge(ine)

            for i in range(len(sinks)):
                gr.remove_vertex(sinks[i])

        if gr._edges:
            print 'cycle...'
            cycle = True

        # print "topo sort result:", not cycle, result
        return not cycle, result



class Vertex(object):
    def __init__(self, graph, model, id_method=None):
        self._model = model
        self._graph = graph


    def __str__(self):
        return self._model.__str__()

    def __repr__(self):
        return self._model.__str__()


    def copy(self, new_graph):
        return Vertex(new_graph, self._model)

    def neighbours(self):
        return self._graph._neighbours(self)

    def out_edges(self):
        return [(self, n) for n in self.neighbours()]

    def in_edges(self):
        return [(ver, self) for ver in self._graph.vertices() if (ver, self) in self._graph._edges_()]
