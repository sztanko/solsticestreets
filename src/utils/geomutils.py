'''
Created on 18 Dec 2013

@author: demetersztanko
'''

def combineSegmentsOld(segments):
    segments_combined = []
    prev_s = None
    current_group = []
    for s in segments:
        if not prev_s:
            current_group.append(s[0])
        if not prev_s or s[0]==prev_s[1]:
            current_group.append(s[1])
        if prev_s and s[0]!=prev_s[1]:
            if len(current_group)>0:
                segments_combined.append(current_group)
            current_group = [s[0], s[1]]
        prev_s = s
    return segments_combined

def combineSegments(segments):
    if len(segments)==0:
        return []
    sg = []
    cur_seg = [segments[0][0],segments[0][1]]
    for i in range(1,len(segments)):
        if segments[i][0]==cur_seg[-1]:
            cur_seg.append(segments[i][1])
        else:
            sg.append(cur_seg)
            cur_seg = [segments[i][0], segments[i][1]]
    sg.append(cur_seg)
    ssg = [[s[0], s[-1]] for s in sg]
    return ssg

def simplifyCombinedSegments(segmentGroup):
    return [[sg[0], sg[-1]] for sg in segmentGroup ]

if __name__ == '__main__':
    segments = [
                [[0,0],[0,1]],
                [[0,1],[1,1]],
                [[1,1],[10,0]],
                [[0,0],[0,1]],
                [[10,0],[10,1]],
                [[10,1],[10,2]],
                [[10,2],[10,3]],
                [[20,0],[20,1]]
                ]
    print segments
    sg = combineSegments(segments)
    print "\n".join([str(i) for i in sg])
    print "\n".join([str(i) for i in simplifyCombinedSegments(sg)])
    pass