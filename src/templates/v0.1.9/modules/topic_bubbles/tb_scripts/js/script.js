var data_folder = ['data/']
var files = {
        meta: 'meta.csv.zip',
        dt: 'dt.json.zip',
        tw: 'tw.json',
        topic_scaled: 'topic_scaled.csv',
        config: 'config.json'
};

var data = {
};

var gui_elements = {
        'topic': 1,
        'absolute range': false,
        'scaled': false,
        'search for words': '',
        'clear search': clearSearch
};

var simulation;
var centerX, centerY;
var width, height;
var minWordCloudSize = 400;
let forceCollide = d3.forceCollide(function(d) { return (d.clicked)? d.r * 1.2 : d.r + 2; });
var init_nodes;
let scaleColor = d3.scaleSequential(d3.interpolateReds); 
var pack;
var root;
var data_nodes;

var dataDomain;
var scaleRadius;
var scaleValue;

var coloringByKeyword = false;
var valueByKeyword = [];
var isMSIE = false; // check if a web browser is IE
var isFF = false; // check if a web browser is Firefox

var lastTransform;
var zoom;

var searchInput; 

var worker = new Worker('js/worker.min.js');
var expandedWidthScale = 2.3;
var expandedHeightScale = 2.0;

var jsonCachePath = '';

var progressBarWidth;
var progress;
var tooltip;
var params = {};
var docListHeight;

function getParams(url) {
//based on the comments and ideas in https://gist.github.com/jlong/2428561
    var parser = document.createElement('a');
    parser.href = url;
    var queries = parser.search.replace(/^\?/, '').split('&');
    var params = {};
    queries.forEach(function(q) {
        var split = q.split('=');
        params[split[0]] = split[1];
    });

    return params;
}

function load() {

    params = getParams(window.location.href);
    params['on'] = false;

    if(typeof params['topicNum'] != 'undefined') {
        params['on'] = true;
        params['nodeID'] = parseInt(params['topicNum']) - 1;
        params['expand'] = ((typeof params['expand'] != 'undefined') && (params['expand'] == 1));
    }

    var infoView = document.getElementById('info-view');
    var infoButton = document.getElementById('info');
    var infoClose = document.getElementById('info-close');

    info.onclick = function() {
        infoView.style.display = "block";
    }

    infoClose.onclick = function() {
        infoView.style.display = "none";
    }

    window.onclick = function(e) {
        if (e.target == infoView) {
            infoView.style.display = "none";
        }
    }

    worker.fs = d3.map();
    worker.onmessage = function(e) {
        var i = worker.fs.get(e.data.what);
        if (i) {
            i(e.data.result);
        }
    };

    worker.callback = function(e, i) {
        worker.fs.set(e, i);
    };

    var ua = window.navigator.userAgent;
    isFF = (ua.indexOf('Firefox') > 0);
    isMSIE = (ua.indexOf('MSIE ') > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./));
    
    var container = d3.select('.container').node();
    var header = d3.select('.header').node();
    container.style.height = (window.innerHeight - header.offsetHeight) + 'px';
    
    var svg = d3.select('svg');
    svgClientNode = (isFF)? svg.node().parentNode : svg.node();
    width = svgClientNode.clientWidth;
    height = svgClientNode.clientHeight;

    var w = Math.max(200, width * 0.3);
    var h = 20;
    progressBarWidth = w;

    var svgDefs = svg.append('defs');
    var progressGradient = svgDefs.append('linearGradient')
                                .attr('id', 'progressGradient');

    progressGradient.append('stop')
                .attr("stop-color", "rgb(254, 234, 225)")
                .attr('offset', '0');

    progressGradient.append('stop')
                .attr("stop-color", "rgb(217, 39, 35)")
                .attr('offset', '1');

    var g = svg.append('g')
                .attr('class', 'progress');

    g.append('rect')
        .attr('rx', 10)
        .attr('ry', 10)
        .attr('fill', 'gray')
        .attr('height', h)
        .attr('width', w)
        .attr('x', (width - w) * 0.5)
        .attr('y', (height - h) * 0.5);

    progress = g.append('rect')
                .attr('rx', 10)
                .attr('ry', 10)
                .attr('fill', 'url(#progressGradient)')
                .attr('height', h)
                .attr('width', 10)
                .attr('x', (width - w) * 0.5)
                .attr('y', (height - h) * 0.5);
                    
    g.append('text')
        .attr('fill', 'dark gray')
        .attr('x', (width - w) * 0.5 + 10)
        .attr('y', (height) * 0.5)
        .style('text-anchor', 'start')
        .style('dominant-baseline', 'central')
        .text('Loading data...');

    loadData(data_folder[0] + files.topic_scaled, function(e, i) {
        if (typeof i === 'string') {
            setTopicScaled(i);

            progress.transition().duration(500).attr('width', function() {
                 return progressBarWidth * 0.25;
            });

            loadData(data_folder[0] + files.tw, function(e, i) {
                if (typeof i === 'string') {
                    setTw(i);

                    progress.transition().duration(500).attr('width', function() {
                        return progressBarWidth * 0.50;
                    });

                    loadData(data_folder[0] + files.dt, function(e, i) {
                        
                        loadData(data_folder[0] + files.config, function(e, i) {

                            if(typeof i === 'string') {
                                var config = JSON.parse(i);
                                jsonCachePath = config.json_cache_path;
                            } else {
                                console.log('Unable to load a file ' + files.config);            
                            }
                        })

                        progress.transition().duration(500).attr('width', function() {
                            return progressBarWidth * 0.75;
                        });

                        setDt(i, function(e) {
                            if (e) {
                                loadData(data_folder[0] + files.meta, function(e, i) {
                                    if (typeof i === 'string') {
                                       
                                        progress.transition().duration(500).attr('width', function() {
                                            return progressBarWidth * 1;
                                        }).on('end', function() {
                                            d3.select('.progress').remove();
                                            setMeta(i);
                                        });

                                    } else {
                                        view.error('Unable to load a file ' + files.meta)
                                    }
                                });
                            } else {
                                console.log('Unable to load a file ' + files.dt)
                            }
                        });

                        
                    });
                } else {
                    console.log('Unable to load a file ' + files.tw);
                }
            });
        } else {
            console.log('Unable to load a file ' + files.topic_scaled);
        }
    });
};

function loadData(e, t) {
    var i, n;
    if (typeof e === 'undefined') {
        return t('target undefined', undefined);
    }
    i = e.replace(/^.*\//, '');
    n = d3.select('#m__DATA__' + i.replace(/\..*$/, ''));
    if (!n.empty()) {
        return t(undefined, JSON.parse(n.html()));
    }
    if (e.search(/\.zip$/) > 0) {
        return d3.buffer(e).then(function(n) {
            var o, r;
            if(n && n.byteLength) {
                o = new JSZip(n);
                r = o.file(i.replace(/\.zip$/, '')).asText();
            }
            return t(e, r);
        })
    }

    return d3.text(e).then(function(data) {
        return t(e, data);
    }).catch(function(error) {
        return t(e, null);
    });
};

function setDt(e, i) {
    if (typeof e !== 'string') {
        i(false)
    }

    worker.callback('set_dt', function(e) {
        //data.dt = e;
        i(e)
    });

    worker.postMessage({
        what: 'set_dt',
        dt: JSON.parse(e)
    });
}

function setMeta(e) {
    var i = e.replace(/^\n*/, "").replace(/\n*$/, "\n");
    
    data.docs = d3.csvParseRows(i, function(e, i) {
            
        var d = new Date(e[6].trim())
        if(d == 'Invalid Date')
            d = new Date();

        var n;
        n = {
            doi: e[0].trim(),
            title: e[1].trim(),
            authors: e[2].trim(),
            journal: e[3].trim(),
            volume: e[4].trim(),
            issue: e[5].trim(),
            date: d,
            pagerange: e[7].trim().replace(/^p?p\. /, "").replace(/-/g, "???")
        };
        e.slice(8, e.length).forEach(function(e, i) {
            n[t.extra_fields[i] || "X" + String(i)] = e.trim()
        });
        return n;
    });

    init();
    draw();
}

function setTw(e) {
    var tw_json;
    
    if (typeof e !== 'string') {
        return
    }
    tw_json = JSON.parse(e);

    var alpha = tw_json.alpha;

    data.tw = tw_json.tw.map(function(e, n) {
        
        var v = 0;
        var w = e.words.map(function(i, n) {
            v += e.weights[n];
            return {
                word: i,
                weight: e.weights[n]
            }
        });

        var t = {
            idx: n,
            name: 'Topic ' + (n + 1),
            weight: v,
            alpha: tw_json.alpha[n],
            words: w
        }
        return t;
    }); 
};  

function setTopicScaled(e) {
    var i;
    if (typeof e !== 'string') {
        return
    }

    i = e.replace(/^\n*/, '').replace(/\n*$/, '\n');
    data.topic_scaled = d3.csvParseRows(i, function(d) {
        return d.map(parseFloat)
    });
};

//Text wrapping based on https://bl.ocks.org/mbostock/7555321
function wrap(text, width) {

    text.each(function () {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1, // ems
            x = text.attr('x'),
            y = text.attr('y'),
            dy = 0, //parseFloat(text.attr("dy")),
            tspan = text.text(null)
                        .append('tspan')
                        .attr('x', x)
                        .attr('y', y)
                        .attr('dy', dy + 'em')
                        .attr('dominant-baseline', 'text-before-edge');

        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(' '));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(' '));
                line = [word];
                tspan = text.append('tspan')
                            .attr('x', x)
                            .attr('y', y)
                            .attr('dy', ++lineNumber * lineHeight + dy + 'em')
                            .attr('dominant-baseline', 'text-before-edge')
                            .text(word);
            }
        }
    });
}

function showDocsList(topic_idx, docLayer) {

    var leftX = minWordCloudSize * 0.5;
    var topY= -minWordCloudSize * 0.5;

    var docs = data.topic_docs[topic_idx].citations.map(function(d, i) {
                    return {
                                id: data.topic_docs[topic_idx].docs[i].doc,
                                frac: data.topic_docs[topic_idx].docs[i].frac,
                                weight: data.topic_docs[topic_idx].docs[i].weight,
                                citation: d
                            };
                });
    
    var svg = d3.select('svg');
    docLayer.select('.doc-loading').classed('hidden', true);
    var fo = docLayer.append('foreignObject')
            .attr('class', 'fo-list')
            .attr('x', leftX + 10)
            .attr('y', topY + 40)
            .attr('width', minWordCloudSize * (expandedWidthScale - 1) - 2 - 20)
            .attr('height', docListHeight - 50)
            .on('mouseover', function() { svg.on('.zoom', null); })
            .on('mouseout', function() { 
                if(gui_elements.scaled)
                    setSacledZoom(svg);
                else {
                    svg.call(zoom.transform, lastTransform);
                    setNormalZoom(svg); 
                }                
            });

    var div = fo.append('xhtml:div')
                .attr('class', 'linkbox')
                .style('font-size', '12px')
                .style('overflow-y', 'auto')
                .style('word-break', 'break-all')
                .style('word-wrap', 'break-word')
                //.style('background-color', d3.rgb(200, 200, 200, 0.9))
                .style('height', '100%')
                .html(function() {
                    var html = "<ul>";
                    for(var i = 0; i < docs.length; i++) {
                        html += "<li id='" + topic_idx + "-" + i +"' onmouseover='showDocsWeights(); toggleWordsHighlight("+ topic_idx + "," + i + ", " + true + ");'" 
                        + " onmouseleave='toggleWordsHighlight("+ topic_idx + "," + i + "," + false + ");'>"
                        if(jsonCachePath != "")
                           html += "<a href=\"\" onclick='openDocViewer(" + topic_idx + "," + i + "); return false;'>";

                        html += "<span>\"" + docs[i].citation.title + "\", " + docs[i].citation.journal + "</span>";
                        
                        if(jsonCachePath != "")
                            html += "</a>";

                        html += "</li>";
                    }

                    html += "</ul>";

                    return html;
                });
}

function closeDocViewer(topic_idx) {
    if(typeof data.topic_docs[topic_idx] == 'undefined') return;

    let node = d3.select('svg .node[id="node-' + topic_idx +'"]');
    var docViewer = node.select('.doc-viewer');
    var docList = node.select('.doc-list');
    var fo = node.select('.fo-json');

    if(docViewer.classed('hidden') == false) {
        var viewerClose = docViewer.select('.viewer-close');
        viewerClose.classed('hidden', true);
        var openRawJsonFileButton = docViewer.select('.open-rawjson');
        openRawJsonFileButton.classed('hidden', true);

        docList.select('.fo-list')
                .attr('height', docListHeight - 50);                

        d3.transition().duration(100).ease(d3.easePolyOut)
                .tween('closeDocViwer', function() {
                    //d3.select(currentTarget).moveToFront();
                    let srcHeight = docViewer.select('rect').attr('height');
                    let dstHeight = 0;
                    let srcY =  minWordCloudSize * (expandedHeightScale - 0.5) - 2
                    let ir = d3.interpolateNumber(srcHeight, dstHeight);
                    
                    viewerClose.attr('transform', 'translate(0,' + (dstHeight) + ')');
                    openRawJsonFileButton.attr('transform', 'translate(0,' + (dstHeight) + ')');

                    return function(t) {
                        let height = ir(t);
                        docViewer.select('rect').attr('y', srcY - height)
                                                .attr('height', height);

                        fo.attr('y', srcY - height)
                            .attr('height', height);
                    };
                })
                .on('end', function() {
                    docViewer.classed('hidden', true);
                    fo.classed('hidden', true);
                    
                })
                .on('interrupt', function() {
                    docViewer.classed('hidden', true);
                    fo.classed('hidden', true);
    
                });
    }

    let lastClickedDocIndex = data.topic_docs[topic_idx].lastClickedDoc;
    var wordCloud = data.wordCloud[topic_idx].layer;
    
    if(typeof lastClickedDocIndex != 'undefined' && lastClickedDocIndex != -1) {
        var lastLi = docList.select('li[id="' + topic_idx + '-' + lastClickedDocIndex + '"]');
        lastLi.style('font-weight', 'normal');
        
        data.topic_docs[topic_idx].docs[lastClickedDocIndex].clicked = false;

        data.topic_docs[topic_idx].lastClickedDoc = -1;
    }

    data.wordCloud[topic_idx].words.forEach(function(w, i)  {
        wordCloud.select('div[id="' + i + '"]')
                .select('span')
                .style('background-color', 'transparent');
    });
}

function openDocViewer(topic_idx, docIndex) {
    let node = d3.select('svg .node[id="node-' + topic_idx +'"]');
    var docViewer = node.select('.doc-viewer');
    var docList = node.select('.doc-list');
    var fo = node.select('.fo-json');
    var div = fo.select('div');

    var li = docList.select('li[id="' + topic_idx + '-' + docIndex + '"]');

    var linkbox = docList.select('.linkbox').node();

    var openRawJsonFileButton = docViewer.select('.open-rawjson');
    var jsonPath = jsonCachePath + data.topic_docs[topic_idx].citations[docIndex].doi;
    openRawJsonFileButton.select('a').attr('xlink:href', jsonPath);

    if(docViewer.classed('hidden')) {
        docViewer.classed('hidden', false);
        fo.classed('hidden', false);

        var viewerClose = docViewer.select('.viewer-close');

        data.topic_docs[topic_idx].docs[docIndex].clicked = true;

        docList.select('.fo-list')
                            .attr('height', minWordCloudSize * (expandedHeightScale) * 0.2 - 50);

        d3.transition().duration(200).ease(d3.easePolyOut)
                .tween('openDocViewer', function() {
                    //d3.select(currentTarget).moveToFront();
                    let srcHeight = docViewer.select('rect').attr('height');
                    let dstHeight = minWordCloudSize * expandedHeightScale * 0.8;
                    let srcY =  minWordCloudSize * (expandedHeightScale - 0.5) - 2
                    let ir = d3.interpolateNumber(srcHeight, dstHeight);
                    
                    viewerClose.attr('transform', 'translate(0,' + (-dstHeight) + ')');
                    openRawJsonFileButton.attr('transform', 'translate(0,' + (-dstHeight) + ')');
                    
                    return function(t) {
                        let height = ir(t);
                        docViewer.select('rect').attr('y', srcY - height)
                                                .attr('height', height);

                        fo.attr('y', srcY - height + 25)
                            .attr('height', height - 30);
                    };
                })
                .on('end', function() {
                    viewerClose.classed('hidden', false);
                    openRawJsonFileButton.classed('hidden', false);

                    linkbox.scrollTop = li.node().offsetTop;
                    
                    if(typeof data.topic_docs[topic_idx].docs[docIndex].jsonRendered != 'undefined') {
                        div._groups[0][0].innerHTML = data.topic_docs[topic_idx].docs[docIndex].jsonRendered;
                    } else if(typeof data.topic_docs[topic_idx].docs[docIndex].json != 'undefined') {
                        $(div._groups[0][0]).jsonViewer(data.topic_docs[topic_idx].docs[docIndex].json);
                        data.topic_docs[topic_idx].docs[docIndex].jsonRendered = div._groups[0][0].innerHTML;
                    }

                })
                .on('interrupt', function() {
                    viewerClose.classed('hidden', false);
                    openRawJsonFileButton.classed('hidden', false);
                    linkbox.scrollTop = li.node().offsetTop;

                    if(typeof data.topic_docs[topic_idx].docs[docIndex].jsonRendered != 'undefined') {
                        div._groups[0][0].innerHTML = data.topic_docs[topic_idx].docs[docIndex].jsonRendered;
                    } else if(typeof data.topic_docs[topic_idx].docs[docIndex].json != 'undefined') {
                        $(div._groups[0][0]).jsonViewer(data.topic_docs[topic_idx].docs[docIndex].json);
                        data.topic_docs[topic_idx].docs[docIndex].jsonRendered = div._groups[0][0].innerHTML;
                    }
                });
    } else {
        if(typeof data.topic_docs[topic_idx].docs[docIndex].jsonRendered != 'undefined') {
            div._groups[0][0].innerHTML = data.topic_docs[topic_idx].docs[docIndex].jsonRendered;
        } else if(typeof data.topic_docs[topic_idx].docs[docIndex].json != 'undefined') {
            $(div._groups[0][0]).jsonViewer(data.topic_docs[topic_idx].docs[docIndex].json);
            data.topic_docs[topic_idx].docs[docIndex].jsonRendered = div._groups[0][0].innerHTML;
        }
    }
    
    let lastClickedDocIndex = data.topic_docs[topic_idx].lastClickedDoc;

    data.topic_docs[topic_idx].lastClickedDoc = docIndex;
    var wordCloud = data.wordCloud[topic_idx].layer;

    if(typeof lastClickedDocIndex != 'undefined' && lastClickedDocIndex != -1) {
        var lastLi = docList.select('li[id="' + topic_idx + '-' + lastClickedDocIndex + '"]');
        lastLi.style('font-weight', 'normal');
        let lastMatched = data.topic_docs[topic_idx].docs[lastClickedDocIndex].matchedWords;

        if(typeof lastMatched != 'undefined') {
            lastMatched.forEach(function(m) {
                wordCloud.select('div[id="' + m.wordCloudIndex + '"]')
                            .select('span')
                            .style('background-color', 'transparent');
            });
        }
    }

    let matched = data.topic_docs[topic_idx].docs[docIndex].matchedWords;
    if(typeof matched != 'undefined') {
        matched.forEach(function(m) {
            wordCloud.select('div[id="' + m.wordCloudIndex + '"]')
                        .select('span')
                        .style('background-color', d3.rgb(255, 100, 100, 0.7));
        });
    }

    li.style('font-weight', 'bold');
}

function showDocsWeights() {

}

function highlightingWords(words, wordCloud, on) {
    words.forEach(function(m) {
        wordCloud.select('div[id="' + m.wordCloudIndex + '"]')
                    .select('span')
                    .style('border-style', (on)? 'dashed': 'none');
    });
}

function toggleWordsHighlight(topic_idx, docIndex, on) {
    if(jsonCachePath == "") return;

    var wordCloud = data.wordCloud[topic_idx].layer;
    var matched = [];
    
    if(on) {   
        if(typeof data.topic_docs[topic_idx].docs[docIndex].json == 'undefined') {
            var jsonPath = jsonCachePath + data.topic_docs[topic_idx].citations[docIndex].doi;
            fetch(jsonPath).then(function(text) { 
               text.json().then(function(json) { 
                    
                    data.topic_docs[topic_idx].docs[docIndex].json = json;
                    var content = '';

                    if(typeof json['content'] != 'undefined') content = json['content'];
                    else if(typeof json['content-wiki-p10'] != 'undefined') content = json['content-wiki-p10'];

                    data.wordCloud[topic_idx].words.forEach(function(w, i) {
                        var reg = '\\b' + w.text + '\\b';
                        if(content.search(new RegExp(reg, 'i')) != -1) {
                            matched.push({word: w.text, wordCloudIndex: i});
                        }
                    });
                    data.topic_docs[topic_idx].docs[docIndex].matchedWords = matched;
                    highlightingWords(matched, wordCloud, on);

                    let clicked = data.topic_docs[topic_idx].docs[docIndex].clicked;
                    if(typeof clicked != 'undefined' && clicked) {
                        openDocViewer(topic_idx, docIndex);
                    }
                });
            });
        } else {
            matched = data.topic_docs[topic_idx].docs[docIndex].matchedWords;
            highlightingWords(matched, wordCloud, on);
        }
    } else {
        matched = data.topic_docs[topic_idx].docs[docIndex].matchedWords;
        
        if(typeof mached != 'undefined') highlightingWords(matched, wordCloud, on);
        else {
            data.wordCloud[topic_idx].words.forEach(function(w, i)  {
                
                wordCloud.select('div[id="' + i + '"]')
                        .select('span')
                        .style('border-style', 'none');
            });
        }
    }
}

function showSources(topic_idx, sourceLayer) {
    var sources = [];
    data.topic_docs[topic_idx].citations.forEach(function(d, i) {

        var name = d.journal;
        // var substringIndex = name.indexOf(' (');
        // if(substringIndex != -1) name = name.slice(0, substringIndex);
        var s = sources.find(function(d) {
            return d.name == name;
        });

        if(typeof s === 'undefined') {
            s = {name: name, weight: 0, docsInfo:[], highlighted:false};
            sources.push(s);
        }
        var w = data.topic_docs[topic_idx].docs[i].weight;
        s.weight += w;
        s.docsInfo.push({index:i, weight:w});
    });

    sources.forEach(function(s) {
        s.docsInfo.forEach(function(a){
            a.ratio = a.weight / s.weight;
        });
    });

    sources.sort(function(a, b) { return b.weight - a.weight; });
    data.topic_sources[topic_idx] = sources;
    var weights = sources.map(function(d) { return d.weight});

    var x = d3.scaleBand()
            .range([0, minWordCloudSize * 0.7])
            .domain(sources.map(function(d) {
                return d.name;
            }))
            .padding(1);
    
    var labelWrap = function() {
        var label = d3.select(this);
        var textLength = label.node().getComputedTextLength();
        var text = label.text();

        while (textLength > (120) && text.length > 0) {
            text = text.slice(0, -1);
            label.text(text + '...');
            textLength = label.node().getComputedTextLength();
        }
    }

    var svg = d3.select('svg');
    var xAxis = svg.append('g')
        .attr('id', 'xAxis')
        .attr('transform', 'translate(-' + (minWordCloudSize * 0.30) + ', ' + (minWordCloudSize + 50) + ')')
        .call(d3.axisBottom(x));

    xAxis.selectAll('text')
        .attr('transform', 'translate(-10, 0)rotate(-45)')
        .style('font-size', '10px')
        .style('text-anchor', 'end')
        .each(labelWrap);

    sourceLayer.node().appendChild(xAxis.node().cloneNode(true));
    xAxis.remove();

    sourceLayer.select('.source-loading').classed('hidden', true);

    sourceLayer.select('g[id="xAxis"]')
            .selectAll('.tick')
            .on('mouseover', function(d, i) {
                d3.select(this).select('text')
                            .style('font-weight', 'bold')
                            .style('cursor', 'default');
                toggleDocsHighlight(topic_idx, sources[i].docsInfo, true);
            })
            .on('mouseleave', function(d, i) {
                d3.select(this).select('text').style('font-weight', 'normal');
                if(!sources[i].highlighted) {
                    toggleDocsHighlight(topic_idx, sources[i].docsInfo, false);   
                }
            });

    var y = d3.scaleLinear()
            .domain([0, d3.max(weights) * 1.1])
            .range([minWordCloudSize * 0.5 - 25, 0]);

    var g = sourceLayer.append('g')
        .attr('transform', 'translate(-' + (minWordCloudSize * 0.30) + ', ' + (minWordCloudSize * 0.5 + 75) + ')')
        .call(d3.axisLeft(y).tickPadding(20))
       
    g.selectAll('text')
        .style('font-size', '10px');

    sourceLayer.append('text')
        .attr('transform', 'translate(-' + (minWordCloudSize * 0.30) + ', ' + (minWordCloudSize * 0.5 + 70) + ')')
        .style('font-size', '10px')
        .style('text-anchor', 'end')
        .text('Weight');

    var lines = g.selectAll('source-lines')
        .data(sources)
        .enter()
        .append('g')
        .on('mouseover', function(d) {
                tooltip.style('visibility', 'visible')
                        .style('left', (d3.event.pageX + 10) + 'px')
                        .style('top', (d3.event.pageY - 10) + 'px')
                        .html(d.name);
                d3.select(this).style('stroke-width', 3)
                                .style('cursor', 'pointer');
                
                toggleDocsHighlight(topic_idx, d.docsInfo, true);
            })
            .on('mousedown', function(d) {
                d.highlighted = !d.highlighted;
                d3.event.stopPropagation();
            })
            .on('mouseleave', function(d) {
                tooltip.style('visibility', 'hidden');
                
                if(!d.highlighted) {
                    toggleDocsHighlight(topic_idx, d.docsInfo, false);
                    d3.select(this).style('stroke-width', 1);
                }
            });

    lines.append('line')
            .attr('x1', function(d) { return x(d.name); })
            .attr('x2', function(d) { return x(d.name); })
            .attr('y1', function(d) { return y(d.weight); })
            .attr('y2', y(0))
            .attr('stroke', 'grey');
    
    lines.append('circle')
            .attr('cx', function(d) { return x(d.name); }) 
            .attr('cy', function(d) { return y(d.weight); })
            .attr('r', 5)
            .style('fill', d3.rgb(0, 200, 255, 0.7))
            .attr('stroke', 'black');
}

function toggleDocsHighlight(topic_idx, docs, on) {
    docs.forEach(function(d) {
        var li = d3.select('li[id="' + topic_idx + '-' + d.index + '"]');
        if(on)
            li.classed('highlighted', true)
                .style('background-color', d3.rgb(0, 200, 255, 0.9 * d.ratio + 0.1));
        else li.classed('highlighted', false)
                .style('background-color', 'transparent');
    });

    data

}

function topicDocs(topic_idx, num, docListLayer, sourceLayer) {
    if(typeof data.topic_docs === 'undefined')
        data.topic_docs = {};
    
    if(typeof data.topic_sources === 'undefined')
        data.topic_sources = {};

    if(typeof data.topic_docs[topic_idx] != 'undefined') {
        showDocsList(topic_idx, docListLayer);
        showSources(topic_idx, sourceLayer);
        return;
    }

    var result = function(d) {
        //console.log(d);
        data.topic_docs[topic_idx] = {
            t: topic_idx,
            docs: d,
            citations: d.map(function(e) {
                return data.docs[e.doc];
            }),
            weight: d3.sum(d, function(e) {
                return e.weight;
            })
        };

        showDocsList(topic_idx, docListLayer);
        showSources(topic_idx, sourceLayer);
    }

    worker.callback("topic_docs/" + topic_idx + "/" + num, result);
    worker.postMessage({
        what: "topic_docs",
        t: topic_idx,
        n: num
    });
}

function ticked() {
    var svg = d3.select('svg');
    var node = svg.selectAll('.node')
    
    if(gui_elements.scaled == false) {
        node.attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; });
    }
    
    // console.log(node.filter((l,i) => l.idx == 53).data()[0]);

    node.select('rect')
        .attr('rx', function(d) { return d.r * d.borderRatio; })
        .attr('ry', function(d) { return d.r * d.borderRatio; })
        .attr('width', function(d) { return (d.expanded)? minWordCloudSize * expandedWidthScale : d.r * 2; })
        .attr('height', function(d) { return (d.expanded)? minWordCloudSize * expandedHeightScale : d.r * 2; })
        .attr('x', function(d) { return d.r * -1; })
        .attr('y', function(d) { return d.r * -1; })
        .style('fill', function(d) { return scaleColor(scaleValue(d.value)); });
    // .style('fill', function(d) { return scaleColor(scaleValue(coloringByKeyword? valueByKeyword[d.idx].value : d.value)));
    //
}

function init() {
    if(typeof data.tw == 'undefined') return;
    
    centerX = width * 0.5;
    centerY = height * 0.5;
    let strength = 0.05;

    pack = d3.pack()
        .size([width, height])
        .padding(0);

    simulation = d3.forceSimulation()
            .force('charge', d3.forceManyBody())
            .force('collide', forceCollide)
            .force('x', d3.forceX(centerX).strength(strength))
            .force('y', d3.forceY(centerY).strength(strength))
            .on('tick', ticked);

    root = d3.hierarchy({ children: data.tw })
            .sum(function(d) { return d.alpha; });

    setMappingScale();

    pack.radius(function(d) { return scaleRadius(d.value); });
    
    data_nodes = pack(root).leaves().map(function(node) {
        const data = node.data;
        //console.log(data.alpha + ' ' + node.r + ' ' + scaleRadius(data.alpha), data.words);
        return {
            x: centerX + (node.x - centerX) * 3,
            y: centerY + (node.y - centerY) * 3,
            r: 0,
            borderRatio: 1,
            idx: data.idx,
            radius: node.r,
            value: node.value,
            weight: data.weight,
            words: data.words,
            name: data.name,
            clicked: false,
            expanded: false
        }
    });

    data.wordCloud = new Array();
    data.searchedWords = new Array();
}

function drawLegend() {

    var svg = d3.select('svg');

    var colorScale = d3.scaleSqrt()
      .domain(dataDomain)
      .range([scaleColor(scaleValue(dataDomain[0])), scaleColor(scaleValue(dataDomain[1]))]);

    svg.append('g')
      .attr('class', 'legend-color')
      .attr('transform', 'translate(' + [20, height - 120] + ')');
    
    svg.append('g')
      .attr('class', 'legend-size')
      .attr('transform', 'translate(' + [100, height - 100] + ')');

    svg.append('g')
      .attr('class', 'legend-search')
      .attr('transform', 'translate(' + [200, height - 120] + ')');

    var legendLinear = d3.legendColor()
      .labelFormat(d3.format('.2f'))
      .cells(5)
      .labelOffset(10)
      .title('Alpha Range')
      .scale(colorScale);
      

    let sizeScale = d3.scaleOrdinal()
            .domain(['low', 'high'])
            .range([5, 20] );
    
    let legendSize = d3.legendSize()
            .scale(sizeScale)
            .shape('circle')
            .shapePadding(40)
            .labelOffset(20)
            .labelAlign('end');

    svg.select('.legend-color')
      .call(legendLinear);

    svg.select('.legend-size')
      .call(legendSize);
}

function setMappingScale() {
    if(typeof data.alphaRange == 'undefined')
        data.alphaRange = [d3.min(data.tw, function(d) { return +d.alpha; }), d3.max(data.tw, function(d) { return +d.alpha; })];

    var isAbsoluteValueRange = gui_elements['absolute range'];

    dataDomain = isAbsoluteValueRange? [0, 1] : data.alphaRange;
    scaleRadius = d3.scaleSqrt().domain(dataDomain).range([20, 80]);
    scaleValue = d3.scaleSqrt().domain(dataDomain).range([0, 0.7]);
}

function draw() {
    // based on the bubble chart example, https://naustud.io/tech-stack/ 
    var svg = d3.select('svg');

    svg.style('cursor', 'move');
    var g = svg.append('g');
    zoom = d3.zoom();
    lastTransform = d3.zoomIdentity;
    setNormalZoom(svg);

    tooltip = d3.select('body')
        .append('div')
        .classed('tooltip', true)
        .style('position', 'absolute')
        .style('left', 0)
        .style('top', 0)
        .style('visibility', 'hidden')
        .style('background-color', 'rgba(0, 0, 0, 0.5)')
        .style('border', '0px')
        .style('padding', '5px')
        .style('min-width', '50px')
        .style('height', '15px')
        .style('font-size', '12px')
        .style('color', 'white')
        .style('line-height', '6px')
        .style('text-align', 'center');

    var node = g.selectAll('.node')
        .data(data_nodes)
        .enter().append('g')
        .attr('id', function(d) { return 'node-' + d.idx; })
        .attr('class', 'node')
        .call(d3.drag()
                .on('start', function(d) {
                    if(gui_elements.scaled) return;
                    if (!d3.event.active) simulation.alphaTarget(0.2).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on('drag', function(d) {
                    d.fx = d3.event.x;
                    d.fy = d3.event.y;
                    if(!d.clicked) tooltip.style('visibility', 'hidden');
                })
                .on('end', function(d) {
                    if (!d3.event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                    if(!d.clicked) tooltip.style('visibility', 'visible');
                }));

    simulation.nodes(data_nodes);

    var rect = node.append('rect')
        .attr('id', function(d) { return d.idx; })
        .attr('rx', 0)
        .attr('ry', 0)
        .attr('width', 0)
        .attr('height', 0)
        .style('fill', function(d) { return scaleColor(scaleValue(d.value)); })
        .style('cursor', 'pointer')
        .style('stroke', 'rgb(0,0,0)')
        .style('stroke-width', 0)
        .transition().duration(2000).ease(d3.easeElasticOut)
                .tween('circleIn', function(d) {
                    let i = d3.interpolateNumber(0, d.radius);

                    return function(t) {
                        d.r = i(t);
                        simulation.force('collide', forceCollide);
                    }
                })
                .on('end', function(d) {
                    if(params['on'] && params['nodeID'] == d.idx) {
                        var nodeTarget = this.parentNode;
                        d3.select(nodeTarget).dispatch('click');
                    }
                })
    
    node.append('clipPath')
        .attr('id', function(d) { return "clip-" + d.idx; })
        .append('rect')
            .attr('rx', function(d) { return d.radius * d.borderRatio; })
            .attr('ry', function(d) { return d.radius * d.borderRatio; })
            .attr('width', function(d) { return d.radius * 2; })
            .attr('height', function(d) { return d.radius * 2; })
            .attr('x', function(d) { return d.radius * -1; })
            .attr('y', function(d) { return d.radius * -1; });

    // node.append('text')
    //     .classed('topic_name', true)
    //     .attr('clip-path', function(d) { return "url(#clip-" + d.idx; })
    //     .selectAll('tspan')
    //     .data(function(d) { return d.name.split(); })
    //     .enter().append('tspan')
    //         .style('cursor', 'pointer')
    //         .text(function(name) { return name; });

    node.append('g')
        .classed('topic_name', true)
        .style('cursor', 'pointer')
        .attr('clip-path', function(d) { return "url(#clip-" + d.idx + ")"; })
        .append('foreignObject')
                .on('mouseover', function(d) {
                    if(d.clicked) return;

                    tooltip.style('visibility', 'visible')
                            .style('left', (d3.event.pageX + 5) + 'px')
                            .style('top', (d3.event.pageY + 5) + 'px')
                            .html(d.value.toFixed(4));
                    var rect = node.select('rect[id="' + d.idx + '"]');
                    rect.style('stroke-width', 3);
                })
                .on('mousemove', function(d) {
                    if(d.clicked) return;

                    tooltip.style('left', (d3.event.pageX + 5) + 'px')
                            .style('top', (d3.event.pageY + 5) + 'px');
                })
                .on('mouseleave', function(d) {                    
                    tooltip.style('visibility', 'hidden');
                    var rect = node.select('rect[id="' + d.idx + '"]');
                    rect.style('stroke-width', 0);
                })
                .attr('x', function(d) { return -d.radius;})
                .attr('y', function(d) { return -d.radius;})
                .attr('width', function(d) { return d.radius * 2;})
                .attr('height', function(d) { return d.radius * 2;})
                .append('xhtml:div')
                    .style('line-height', function(d) { return d.radius * 2 + 'px';})
                    .style('text-align', 'center')
                    .style('font-size', '13px')
                    .style('white-space', 'nowrap')
                    .html(function(d) { return d.name; });
    
    d3.selection.prototype.moveToFront = function() {  
      return this.each(function(){
        this.parentNode.appendChild(this);
      });
    };
    
    d3.selection.prototype.moveToBack = function() {  
        return this.each(function() { 
            var firstChild = this.parentNode.firstChild; 
            if (firstChild) { 
                this.parentNode.insertBefore(this, firstChild); 
            } 
        });
    };

    // based on https://stackoverflow.com/questions/38224875/replacing-d3-transform-in-d3-v4/38230545#38230545
    d3.selection.prototype.getTranslation = function() {
        var transform = this.attr('transform')
        var g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttributeNS(null, 'transform', transform);
        var matrix = g.transform.baseVal.consolidate().matrix;
        return [matrix.e, matrix.f];
    }

    // Word Cloud Implementation
    // based on Jason Davies's library, https://github.com/jasondavies/d3-cloud

    let wordCloudLayer = node.append('g')
                            .classed('wordcloud-overlay hidden', true);
    let leftX = topY = -minWordCloudSize * 0.5;
    let rightX = minWordCloudSize * 0.5;
    let roundOff = (minWordCloudSize * 0.5 - 2) * 0.1;
    
    wordCloudLayer.append('rect')
            .attr('x', leftX + 2)
            .attr('y', topY + 2)
            .attr('rx', roundOff)
            .attr('ry', roundOff)
            .attr('height', minWordCloudSize - 4)
            .attr('width', minWordCloudSize - 4)
            .style('fill', d3.rgb(255, 255, 255));
    
    
    var closeButton = wordCloudLayer.append('g');
    let buttonRadius = 10;
    let crossOffset = buttonRadius * 0.5
    let buttonCenterX = rightX - buttonRadius * 2;
    let buttonCenterY = topY + buttonRadius * 2;

    closeButton.append('circle')
            .attr('cx', buttonCenterX)
            .attr('cy', buttonCenterY)
            .attr('r', buttonRadius)
            .style('fill', d3.rgb(255, 0, 0, 0.7))
            .style('cursor', 'pointer');

    closeButton.on('click', function(selectedNode) {
                let selectedTarget = node.filter(function(d, i) { return (d.idx === selectedNode.index); });
                if(selectedNode.expanded) { 
                    toggleFullView(selectedNode, selectedTarget);
                }
                closeBubble(selectedNode, selectedTarget);
            });

    var cross = closeButton.append('g');

    cross.style('cursor', 'pointer');

    cross.append('line')
            .attr("x1", buttonCenterX - buttonRadius + crossOffset)
            .attr("y1", buttonCenterY)
            .attr("x2", buttonCenterX + buttonRadius - crossOffset)
            .attr("y2", buttonCenterY);
            
    cross.append('line')
            .attr("x1", buttonCenterX)
            .attr("y1", buttonCenterY - buttonRadius + crossOffset)
            .attr("x2", buttonCenterX)
            .attr("y2", buttonCenterY + buttonRadius  - crossOffset);

    cross.attr("transform", "rotate (45," + buttonCenterX + "," + buttonCenterY + ")");

    cross.style('stroke', 'black')
        .style('stroke-width', 1.5);

    var fo = wordCloudLayer.append('foreignObject')
            .attr('x', -50)
            .attr('y', topY + 10)
            .attr('width', 100)
            .attr('height', 25);
           
    var div = fo.append('xhtml:div')
                .style('line-height', '25px')
                .style('text-align', 'center')
                .style('font-weight', 'bold')
                .style('font-size', '13px')
                .html(function(d) { return d.name; });
    
    var expandButton = wordCloudLayer.append('g').classed('expand-button', true);
    buttonCenterY = topY + minWordCloudSize - buttonRadius * 2;
    expandButton.append('circle')
            .attr('cx', buttonCenterX)
            .attr('cy', buttonCenterY)
            .attr('r', buttonRadius)
            .style('fill', d3.rgb(0, 200, 255, 0.7))
            .style('cursor', 'pointer');
    
    var expandButtonTriangle = expandButton.append('g').classed('expand-triangle', true);
    var symbolGenerator = d3.symbol().type(d3.symbolTriangle).size(20);
    expandButtonTriangle.append('path')
            .classed('triangle-up', true)
            .attr('d',symbolGenerator)
            .attr('transform', 'translate(' +[buttonCenterX + buttonRadius * 0.25, buttonCenterY + buttonRadius * 0.25] + '), rotate(15)')
            .style('fill', 'black')
            .style('cursor', 'pointer');

     expandButtonTriangle.append('path')
            .classed('triangle-down', true)
            .attr('d',symbolGenerator)
            .attr('transform', 'translate(' +[buttonCenterX - buttonRadius * 0.25, buttonCenterY - buttonRadius * 0.25] + '), rotate(-45)')
            .style('fill', 'black')
            .style('cursor', 'pointer');

    expandButton.on('click', function(selectedNode) {
                let selectedTarget = node.filter(function(d, i) { return (d.idx === selectedNode.index); });
                toggleFullView(selectedNode, selectedTarget);
            });

    leftX = minWordCloudSize * 0.5;
    topY = -minWordCloudSize * 0.5;

    let docLists = node.append('g')
                        .classed('doc-list hidden', true);
    docListHeight = minWordCloudSize * expandedHeightScale - 4;
    
    let docListWidth = minWordCloudSize * (expandedWidthScale - 1) - 2;

    docLists.append('rect')
            .attr('x', leftX)
            .attr('y', topY + 2)
            .attr('rx', roundOff)
            .attr('ry', roundOff)
            .attr('height', docListHeight)
            .attr('width', docListWidth)
            .style('fill', d3.rgb(255, 255, 255, 0.9));

    var fo = docLists.append('foreignObject')
            .attr('x', leftX + docListWidth * 0.5 - 125)
            .attr('y', topY + 10)
            .attr('width', 250)
            .attr('height', 25);
           
    var div = fo.append('xhtml:div')
                .style('line-height', '25px')
                .style('text-align', 'center')
                .style('font-weight', 'bold')
                .style('font-size', '13px')
                .style('cursor', 'default')
                .html('Top 20 Documents<br><h2>Loading the list of documents...</h2>');

    docLists.append('text')
            .classed('doc-loading', true)
            .attr('x', leftX + (minWordCloudSize * (expandedWidthScale - 1) - 2) * 0.5)
            .attr('y', (minWordCloudSize * (expandedWidthScale - 1) - 2) * 0.5)
            .style('text-anchor', 'middle')
            .style('font-size', '20px')
            .text('Loading the list of documents...');

    let docViewer = node.append('g')
                        .classed('doc-viewer hidden', true);
    let docViewerY = topY + minWordCloudSize * expandedHeightScale - 2;

    docViewer.append('rect')
            .attr('x', leftX)
            .attr('y', docViewerY)
            .attr('rx', roundOff)
            .attr('ry', roundOff)
            .attr('height', 0)
            .attr('width', docListWidth)
            .style('fill', d3.rgb(255, 255, 255))
            .style('stroke', d3.rgb(100, 100, 100, 0.7));

    var fo = docViewer.append('foreignObject')
            .classed('fo-json hidden', true)
            .attr('x', leftX + 10)
            .attr('y', docViewerY)
            .attr('width', docListWidth - 20)
            .attr('height', 0)
            .on('mouseover', function() { svg.on('.zoom', null); })
            .on('mouseout', function() { 
                if(gui_elements.scaled)
                    setSacledZoom(svg);
                else {
                    svg.call(zoom.transform, lastTransform);
                    setNormalZoom(svg); 
                }                
            });

    var div = fo.append('xhtml:div')
                .style('font-size', '13px')
                .style('overflow-y', 'auto')
                .style('word-break', 'break-all')
                .style('word-wrap', 'break-word')
                .style('height', '100%')
                .html('<h2>No public information is available for this document.</h2>');

    var viewerCloseButton = docViewer.append('g')
                                .classed('viewer-close hidden', true);
    
    buttonCenterX = leftX + buttonRadius * 2;
    buttonCenterY = docViewerY + buttonRadius * 2;

    viewerCloseButton.append('circle')
            .attr('cx', buttonCenterX)
            .attr('cy', buttonCenterY)
            .attr('r', buttonRadius)
            .style('fill', d3.rgb(100, 100, 100, 0.7))
            .style('cursor', 'pointer');
    var viewerCloseButtonTriangle = viewerCloseButton.append('g');
    viewerCloseButtonTriangle.append('path')
            .attr('d', symbolGenerator)
            .attr('transform', 'translate(' +[buttonCenterX, buttonCenterY] + ')rotate(60)')
            .style('fill', 'black')
            .style('cursor', 'pointer');

    viewerCloseButton.on('click', function(selectedNode) {
                closeDocViewer(selectedNode.idx);
            });

    let buttonWidth = 160;
    let buttonHeight = buttonRadius * 2;
    let buttonX = buttonCenterX + buttonRadius + 8;
    let buttonY = topY + minWordCloudSize * expandedHeightScale - 2 + buttonRadius;

    var openRawJsonFileButton = docViewer.append('g')
                                .classed('open-rawjson hidden', true);
    openRawJsonFileButton.append('a').attr('target', '_blank')
                        .append('rect')
                        .attr('x', buttonX)
                        .attr('y', buttonY)
                        .attr('rx', buttonHeight * 0.5)
                        .attr('ry', buttonHeight * 0.5)
                        .attr('width', buttonWidth)
                        .attr('height', buttonHeight)
                        .style('fill', d3.rgb(255, 255, 255, 1))
                        .style('stroke', d3.rgb(100, 100, 100, 0.7))
                        .style('cursor', 'pointer');
    
    openRawJsonFileButton.append('text')
                        .attr('x', buttonX + buttonWidth * 0.5)
                        .attr('y', buttonY + buttonHeight * 0.5)
                        .attr('text-anchor', 'middle')
                        .attr("dy", ".35em")
                        .style('fill', d3.rgb(100, 100, 100, 0.7))
                        .style('font-size', '12px')
                        .style('pointer-events', 'none')
                        .text('View JSON in New Window');

    leftX = -minWordCloudSize * 0.5;
    topY= minWordCloudSize * 0.5;
    
    let sources = node.append('g')
                        .classed('source-view hidden', true);

    sources.append('rect')
            .attr('x', leftX + 2)
            .attr('y', topY)
            .attr('rx', roundOff)
            .attr('ry', roundOff)
            .attr('height', minWordCloudSize * expandedHeightScale - minWordCloudSize - 2)
            .attr('width', minWordCloudSize - 4)
            .style('fill', d3.rgb(255, 255, 255, 0.9));

    fo = sources.append('foreignObject')
            .attr('x', leftX + (minWordCloudSize - 4) * 0.5 - 125)
            .attr('y', topY + 10)
            .attr('width', 250)
            .attr('height', 25);
    
    sources.append('text')
            .classed('source-loading', true)
            .attr('x', leftX + (minWordCloudSize - 4) * 0.5)
            .attr('y', topY + (minWordCloudSize * expandedHeightScale - minWordCloudSize  - 2) * 0.5)
            .style('text-anchor', 'middle')
            .style('font-size', '20px')
            .text('Checking the sources of documents...');

    div = fo.append('xhtml:div')
                .style('line-height', '25px')
                .style('text-align', 'center')
                .style('font-weight', 'bold')
                .style('font-size', '13px')
                .style('cursor', 'default')
                .html('Sources of Top 20 Documents');

    var lastTarget = null;
    node.on('click', function(selectedNode) {
        let currentTarget = d3.event.currentTarget;
        if(lastTarget != currentTarget) {
            d3.select(currentTarget).moveToFront();
            if(lastTarget != null) {
                
                var linkbox = d3.select(lastTarget).select('.linkbox').node();
                var nodeData = d3.select(lastTarget).data()[0];
                if(linkbox =! null) nodeData.scrollTop = linkbox.scrollTop;

                d3.select(lastTarget).select('.linkbox').style('overflow-y', 'hidden');
            }
            
            d3.select(currentTarget).select('.linkbox').style('overflow-y', 'auto');

            if(typeof selectedNode.scrollTop != 'undefined'){
                var linkbox = d3.select(currentTarget).select('.linkbox').node();
                linkbox.scrollTop = selectedNode.scrollTop;
            }
        }
        lastTarget = currentTarget;

         if(selectedNode.clicked == true) return;

        selectedNode.clicked = true;

        var rect = node.select('rect[id="' + selectedNode.idx + '"]');
        rect.style('stroke-width', 0);
        
        if(typeof data.wordCloud[selectedNode.idx] == 'undefined') {

            let fontSizeScale = d3.scaleSqrt().domain([0, 1]).range([5, 25]);
            var maxWeight = selectedNode.words[0].weight;
            var words_frequency = selectedNode.words.slice(0, 50).map(function(w) {
                return {
                    text: w.word,
                    size: Math.floor(fontSizeScale(w.weight / maxWeight))
                }
            });

            d3.layout.cloud().size([minWordCloudSize - 15, minWordCloudSize - 50])
                    .timeInterval(10)
                    .words(words_frequency)
                    .padding(5)
                    .rotate(0)
                    .fontSize(function(w) { return w.size; })
                    .on('end', function(words) {
                        data.wordCloud[selectedNode.idx] = {words: words};

                        var layer = wordCloudLayer.filter(function(l,i) { return (l.idx == selectedNode.idx); })
                                                    .append('g')
                                                    .attr('id', 'words');
                                                    
                        data.wordCloud[selectedNode.idx].layer = layer;

                        data.wordCloud[selectedNode.idx].words.forEach(function(w, i) {
                            data.wordCloud[selectedNode.idx].words[i].clicked = false;

                            var fo = layer.append('foreignObject')
                                    .attr('transform', 
                                        'translate(' + [w.x - w.width * 0.5, 20 + w.y - w.height * 0.5] + ')rotate(' + w.rotate + ')')   
                                    .attr('width', w.width)
                                    .attr('height', w.height)
                                    .style('line-height', w.height + 'px');
                           
                            var div = fo.append('xhtml:div')
                                        .attr('id', i)
                                        .style('cursor', 'pointer')
                                        .style('text-align', 'center')
                                        .style('font-size', w.size + 'px')
                                        .attr('width', w.width * 0.5)
                                        .attr('height', w.height * 0.5)
                                        .html('<span class="wordbox">' + w.text + '</span>')
                                        .on('mouseover', function(d) {
                                            
                                            div.style('color', 'blue');
                                            tooltip.style('visibility', 'visible')
                                                .style('left', (d3.event.pageX + 10) + 'px')
                                                .style('top', (d3.event.pageY + 15) + 'px')
                                                .html('Weight: ' + d.words[i].weight
                                                 + '(' + (100 * d.words[i].weight/d.weight).toFixed(2) + '%)');
                                        })
                                        .on('mouseout', function(d) {
                                            div.style('color', 'black')

                                            if(data.wordCloud[selectedNode.idx].words[i].clicked == false) {
                                                div.classed('clicked', false);
                                            }
                                            tooltip.style('visibility', 'hidden')
                                        })
                                        .on('click', function(d) {

                                            // if(data.searchedWords.length > 0)
                                            //     clickedWords = data.searchedWords;

                                            data.wordCloud[selectedNode.idx].words[i].clicked = !data.wordCloud[selectedNode.idx].words[i].clicked;
                                            
                                            if(data.wordCloud[selectedNode.idx].words[i].clicked) {
                                                if(data.searchedWords.indexOf(w.text) == -1) data.searchedWords.push(w.text);
                                                div.style('color', 'black')
                                                    .classed('clicked', true);
                                                
                                            } else {
                                                data.searchedWords = data.searchedWords.filter(function(element) {
                                                                        return element != w.text;
                                                                    });

                                                div.classed('clicked', false);
                                            }

                                            searchKeywords(data.searchedWords, true);
                                        });

                                if(typeof data.searchedWords != 'undefined' && 
                                    data.searchedWords.indexOf(w.text) != -1) {

                                    data.wordCloud[selectedNode.idx].words[i].clicked = true;
                                    div.classed('clicked', true);
                                }
                        });
                    })
                    .start();

                var docListLayer = docLists.filter(function(l,i) { return (l.idx == selectedNode.idx); });
                var sourceLayer = sources.filter(function(l,i) { return (l.idx == selectedNode.idx); });
                topicDocs(selectedNode.idx, 20, docListLayer, sourceLayer);
        }

        d3.event.stopPropagation();
        
        d3.select(currentTarget).selectAll('.arc').classed('hidden', true);
        let currentGroup = d3.select(currentTarget);

        d3.transition().duration(500).ease(d3.easePolyOut)
            .tween('circleToRect', function() {
                //d3.select(currentTarget).moveToFront();
                let ir = d3.interpolateNumber(selectedNode.r, minWordCloudSize * 0.5);
                let irBorder = d3.interpolateNumber(selectedNode.borderRatio, 0.1);
                
                return function(t) {
                    selectedNode.r = ir(t);
                    selectedNode.borderRatio = irBorder(t);

                    if(gui_elements.scaled) {
                        d3.select(currentTarget).select('rect')
                                .attr('rx', function(d) { return d.r * d.borderRatio; })
                                .attr('ry', function(d) { return d.r * d.borderRatio; })
                                .attr('width', function(d) { return (d.expanded)? minWordCloudSize * expandedWidthScale : d.r * 2; })
                                .attr('height', function(d) { return (d.expanded)? minWordCloudSize * expandedHeightScale : d.r * 2; })
                                .attr('x', function(d) { return d.r * -1; })
                                .attr('y', function(d) { return d.r * -1; })
                                .style('fill', function(d) { return scaleColor(scaleValue(d.value)); });
                        
                    } else simulation.force('collide', forceCollide);
                };
            })
            .on('end', function() {
                    simulation.alphaTarget(0);
                    
                    currentGroup.select('.wordcloud-overlay').classed('hidden', false);
                    currentGroup.select('.topic_name').classed('hidden', true);

                    if(params['on'] && params['nodeID'] == selectedNode.idx && params['expand']) {

                        var expandFunc = function() {    
                                
                                let selectedTarget = d3.select(currentTarget);
                                var nodeData = selectedTarget.data()[0];
                                toggleFullView(nodeData, selectedTarget);

                                params['on'] = false;
                            }

                        setTimeout(expandFunc, 1000);
                    }
            })
            .on('interrupt', function() {
                    selectedNode.borderRatio = 0.1;
                    selectedNode.r = centerY * 0.5;
                    simulation.alphaTarget(0);

                    currentGroup.select('.wordcloud-overlay').classed('hidden', false);
                    currentGroup.select('.topic_name').classed('hidden', true);

                    if(params['on'] && params['nodeID'] == selectedNode.idx && params['expand']) {

                        var expandFunc = function() {    
                                
                                let selectedTarget = d3.select(currentTarget);
                                var nodeData = selectedTarget.data()[0];
                                toggleFullView(nodeData, selectedTarget);

                                params['on'] = false;
                            }

                        setTimeout(expandFunc, 1000);
                    }
            });
    });
    
    addGui();
    drawLegend();
}

function toggleArrow(expanded, target) {
    let buttonGroup = target.select('.toggle-full-view');
    let button = target.select('.toggle-full-view rect');
    let buttonCenterX = +button.attr('x') + (+button.attr('width')) * 0.5;
    let buttonCenterY = +button.attr('y') + (+button.attr('height')) * 0.5;

    let angle = (expanded)? 0 : 180;
    buttonGroup.attr("transform", "rotate (" + angle + "," + buttonCenterX + "," + buttonCenterY + ")");
}

function toggleFullView(node, target){
    let rect = target.select('rect');
    
    let button = target.select('.expand-button circle');
    let triangleUp = target.select('.triangle-up');
    let triangleDown = target.select('.triangle-down');
    let buttonCenterX = +button.attr('cx');
    let buttonCenterY = +button.attr('cy');
    let buttonRadius = 10;

    var angle = (node.expanded)? 15 : -45;
    triangleUp.attr('transform', 'translate(' +[buttonCenterX + buttonRadius * 0.25, buttonCenterY + buttonRadius * 0.25] + '), rotate(' + angle + ')');

    angle = (node.expanded)? -45 : 15;
    triangleDown.attr('transform', 'translate(' +[buttonCenterX - buttonRadius * 0.25, buttonCenterY - buttonRadius * 0.25] + '), rotate(' + angle + ')');

    if(node.expanded) closeDocViewer(node.idx);

    d3.transition()
        .duration(200)
        .ease((node.expanded)? d3.easePolyIn : d3.easePolyOut)
        .tween('expandRect', function() {

            if(node.expanded) { 
                target.select('.doc-list').classed('hidden', true);
                target.select('.source-view').classed('hidden', true);
            }

            let irWidth = d3.interpolateNumber(rect.attr('width'), (node.expanded)? node.r * 2 : minWordCloudSize * expandedWidthScale);
            let irHeight = d3.interpolateNumber(rect.attr('height'), (node.expanded)? node.r * 2 : minWordCloudSize * expandedHeightScale);

            return function(t) {

                rect.attr('width', irWidth(t));
                rect.attr('height', irHeight(t));
                if(gui_elements.scaled == false) simulation.force('collide', forceCollide);
            };
        })
        .on('end', function(){
            simulation.alphaTarget(0);
            node.expanded = !node.expanded;
            if(node.expanded) {
                target.select('.doc-list').classed('hidden', false);
                target.select('.source-view').classed('hidden', false);
            }
        })
        .on('interrupt', function() {
            rect.attr('width', (node.expanded)? node.r * 2 : minWordCloudSize * expandedWidthScale);
            rect.attr('height', (node.expanded)? node.r * 2 : minWordCloudSize * expandedHeightScale);
            simulation.alphaTarget(0);
            node.expanded = !node.expanded;
            if(node.expanded) {
                target.select('.doc-list').classed('hidden', false);
                target.select('.source-view').classed('hidden', false);
            }        
        });

}

function closeBubble(node, target){
    d3.transition()
        .duration(500)
        .ease(d3.easePolyOut)
        .tween('rectToCircle', function() {
            let ir = d3.interpolateNumber(node.r, node.radius);
            let irlBorder = d3.interpolateNumber(node.borderRatio, 1);

            if(node.expanded) toggleFullView(node, target);
            
            return function(t) {
                node.r = ir(t);
                node.borderRatio = irlBorder(t);
                
                if(gui_elements.scaled) {
                    target.select('rect')
                            .attr('rx', function(d) { return d.r * d.borderRatio; })
                            .attr('ry', function(d) { return d.r * d.borderRatio; })
                            .attr('width', function(d) { return (d.expanded)? minWordCloudSize * expandedWidthScale : d.r * 2; })
                            .attr('height', function(d) { return (d.expanded)? minWordCloudSize * expandedHeightScale : d.r * 2; })
                            .attr('x', function(d) { return d.r * -1; })
                            .attr('y', function(d) { return d.r * -1; })
                            .style('fill', function(d) { return scaleColor(scaleValue(d.value)); });
                    
                } else simulation.force('collide', forceCollide);
            };
        })
        .on('end', function(){
            target.select('.topic_name').classed('hidden', false);
            target.selectAll('.arc').classed('hidden', false);

            simulation.alphaTarget(0);
            node.clicked = false;
        })
        .on('interrupt', function() {
            target.select('.topic_name').classed('hidden', false);
            target.selectAll('.arc').classed('hidden', false);

            simulation.alphaTarget(0);
            node.clicked = false;
        });

    target.select('.wordcloud-overlay').classed('hidden', true);
}

function setNormalZoom(svg) {
    zoom.scaleExtent([0.3, 1])
        .on('zoom', function() {
            var transform = d3.event.transform;

            svg.select('g').attr('transform', transform);
            lastTransform = transform;
        });
    svg.call(zoom);
}

function setSacledZoom(svg) {
    var aspect = width / height;
    var n = Math.floor(width / (2.1 * Math.sqrt(aspect * data.tw.length)));
    var i = n * 1.8;
    var o = 1.1 * n;

    var xScale = d3.scaleLinear().domain([0, width]).range([o, width - o]);
    var yScale = d3.scaleLinear().domain([height, 0]).range([height - o, o]);
    var nodes = svg.selectAll('.node');

    zoom.scaleExtent([1, 15])
        .on('zoom', function() {
            var transform = d3.event.transform;
            var newX, newY;
            
            nodes.transition().duration(1)
                .attr('transform', function(d) {
                    newX = transform.applyX(xScale(d.scaledInitX));
                    newY = transform.applyY(yScale(d.scaledInitY));

                    return 'translate(' + [newX, newY] + ')';
                });
        });

    svg.call(zoom);
}

var searchLegend = d3.legendColor().labelOffset(10).title('Search Result');
var searchLegendColor = d3.scaleOrdinal();

function searchKeywords(keywords, splitted) {
    
    if(splitted == false) {
        if(keywords == '' || keywords.replace(/\+/g, '') == '') keywords = [];
        else {
            keywords = keywords.split('+').filter(function(element){
                        return element != '';
                    });
        }

        data.searchedWords = keywords;
    }

    var valueForSearchInput = '';
    data.searchedWords.forEach(function(w, wi) {
        valueForSearchInput += w;
        if(wi < data.searchedWords.length - 1)
            valueForSearchInput += '+';
    });

    searchInput.setValue(valueForSearchInput);

    var svg = d3.select('svg');

    var result = [[],];

    let isKeywordEmpty = (keywords.length == 0);
    
    var arc = d3.arc();

    var rect = svg.selectAll('.node rect[id]');
    var arcPath = svg.selectAll('.node path[id]');

    arcPath.remove();
    svg.select('.legend-search').classed('hidden', isKeywordEmpty);

    if(isKeywordEmpty == false) {

        data.tw.forEach(function(d, i) {
            result[i] = [];
            
            
            let weight = d.weight;
            var found = [];
            keywords.forEach(function(kw, ki) {

                if(kw == '') return;
                
                var v = {word: kw, value: 0, index:-1};
                
                let r = d.words.filter(function(w, wi) {
                    if(w.word == kw.trim()) {
                        v.index = wi;
                        return true;
                    }
                    return false;
                });
                
                if(r.length > 0) {
                    v.value = r[0].weight/weight;
                    found.push(v);
                }
            });

            if(found.length == keywords.length)
                result[i] = found;
        });

        searchLegendColor = d3.scaleOrdinal();
        searchLegendColor.domain(keywords)
            .range(keywords.map(function(val, i) {
                return d3.interpolateYlGnBu(1 - (i / (keywords.length)));
            }));

        searchLegend.scale(searchLegendColor);

        var cells = svg.select('.legend-search').call(searchLegend).selectAll('.cell');

        cells.attr('transform', function(d, i) { 
            return 'translate(' + Math.floor(i / 5) * 120 + ',' + ((i % 5) * 17) + ')'; 
        });
    }

    rect.transition().duration(1000).ease(d3.easeElasticOut)
        .tween('circleSearch', function(d) {
            var src = d.r;
            let hasResult = (typeof result[d.idx] != 'undefined' && result[d.idx].length > 0);

            d.radius = (isKeywordEmpty || hasResult)? scaleRadius(d.value) : 0;
            var dst = ((d.clicked && hasResult) || (d.clicked && isKeywordEmpty))? src : d.radius;
            let i = d3.interpolateNumber(src, dst);

            var borderTarget = ((d.clicked && hasResult) || (d.clicked && isKeywordEmpty))? 0.1: 1;
            let irBorder = d3.interpolateNumber(d.borderRatio, borderTarget);

            var parentNode = d3.select(this.parentNode);
            var wordCloudLayer = parentNode.select('.wordcloud-overlay');
            var texts = wordCloudLayer.select('g#words').selectAll('div');

            //if(texts._groups.length != 0) console.log(texts);
            texts.classed('clicked', false);
            
            if(typeof data.wordCloud[d.idx] != 'undefined') {
                data.wordCloud[d.idx].words.forEach(function(w, i) {
                    w.clicked = false;
                });
            }

            // due to that IE does not support clipPath
            if(isMSIE) { 
                parentNode.select('.topic_name').classed('hidden', (d.radius == 0));
            }
            
            //hide a clicked bubble if it has no search keyword
            if(d.clicked && hasResult == false && isKeywordEmpty == false) {
                
                if(d.expanded) {
                    toggleFullView(d, parentNode);
                }

                wordCloudLayer.classed('hidden', true);
                parentNode.select('.topic_name').classed('hidden', false);
                d.clicked = false;
            }

            if(hasResult) {

                result[d.idx].forEach(function(v) {
                    var text = texts.filter(function(t, ti) { return ti == v.index; });
                    text.classed('clicked', true);

                    if(typeof data.wordCloud[d.idx] != 'undefined' && typeof data.wordCloud[d.idx].words[v.index] != 'undefined') {
                        data.wordCloud[d.idx].words[v.index].clicked = true;
                    }
                });

                parentNode.select('.topic_name').classed('hidden', false);
            } else {
                parentNode.select('.topic_name').classed('hidden', (isKeywordEmpty == false)? true: false);
            } 

            return function(t) {
                d.r = i(t);
                if(d.r < 0) d.r = 0;
                d.borderRatio = irBorder(t);

                if(gui_elements.scaled == false) simulation.force('collide', forceCollide);
            }
        })
        .on('end', function(t) {
            
            simulation.alphaTarget(0);
                               
        })
        .on('interrupt', function() {
            
            simulation.alphaTarget(0);
        });

    var nodes = svg.selectAll('.node')

    result.forEach(function(v, i) {

        var start = 0;
        var node = nodes.filter(function(n) { return (n.idx == i); });

        v.forEach(function(kw, ki) {
            
            var end = start + 2 * Math.PI * kw.value;

            node.append('path')
            .classed('arc', true)
            .classed('hidden', function(d) { return d.clicked; })
            .attr('id', function(d) { return d.idx + kw.word + ki; })
            .attr('d', function(d) {

                return arc({
                    innerRadius: 0,
                    outerRadius: scaleRadius(d.value),
                    startAngle:start,
                    endAngle:end
                }); 
            })
            .attr('fill', function(d) { return searchLegendColor(ki); });

            start = end;  
        });
    });
    
    simulation.alphaTarget(0.2).restart();
}

function clearSearch() {
    searchKeywords('', false);
}

function addGui() {
    var gui = new dat.GUI({ autoPlace: false });
    var customContainer = $('.gui').append($(gui.domElement));
    var svg = d3.select('svg');
   
    var topicNum = gui.add(gui_elements, 'topic').min(1).max(data.tw.length).step(1);
    topicNum.__li.classList.remove('has-slider');
    topicNum.domElement.getElementsByClassName('slider')[0].remove();
    topicNum.domElement.getElementsByTagName('input')[0]
                        .addEventListener('mousedown', function(event) { 
                            event.stopPropagation();
                        }, true);

    var input = topicNum.domElement.getElementsByTagName('input')[0];
    input.addEventListener('keydown', function(event) {
        if(event.keyCode !== 13) return;

        var i = input.value;
        var node = svg.select('.node[id="node-' + (i - 1) + '"]');
        var rect = node.select('rect[id="' + (i - 1) + '"]');
        node.moveToFront();

        rect.transition().duration(2000)
            .styleTween('stroke-width', function() { return d3.interpolate(6, 0); })

        var nodeTranslate = node.getTranslation();
        var g = svg.select('g');
        var scale = lastTransform.k;
        var translate = [centerX - nodeTranslate[0] * scale, centerY - nodeTranslate[1] * scale];

        g.attr('transform', 'translate(' + translate + ')' + 
                     ',scale(' + scale + ')');

        lastTransform.x = translate[0];
        lastTransform.y = translate[1];
        lastTransform.k = scale;

        event.stopPropagation();
    }, true);

    var scaled = gui.add(gui_elements, 'scaled');
    
    if(typeof data.topic_scaled != 'undefined' ) {
        scaled.onChange(function() {

            var nodes = svg.selectAll('.node');

            if(gui_elements.scaled) {

                simulation.force('collide', null);

                data.topic_scaled.forEach(function(scaleRatio, i) {

                    var node = nodes.filter(function(l) { return (l.idx == i);} )
                        node.transition().duration(1000)
                            .attr('transform', function(d) {
                                 return 'translate(' + [centerX + width * scaleRatio[0], centerY - height * scaleRatio[1]] + ')'
                            })
                            .on('end', function(d) {
                                d.scaledInitX = centerX + width * scaleRatio[0];
                                d.scaledInitY = centerY - height * scaleRatio[1];
                                setSacledZoom(svg);
                            })
                            .on('interrupt', function(d) {
                                d.scaledInitX = centerX + width * scaleRatio[0];
                                d.scaledInitY = centerY - height * scaleRatio[1];
                                setSacledZoom(svg);
                            });
                });

            } else {
                // simulation.nodes(nodes.data());
                
                simulation.force('collide', forceCollide);
                simulation.alphaTarget(0.2).restart();
                svg.call(zoom.transform, lastTransform);
                setNormalZoom(svg);
            }
        });
    } else {
        scaled.domElement.childNodes[0].disabled = true;
    }


    gui.add(gui_elements, 'absolute range').onChange(function() {

        setMappingScale();
        svg.select('.legend-color').remove();
        svg.select('.legend-size').remove();

        drawLegend();

        var rect = svg.selectAll('.node rect[id]');
        var arcPath = svg.selectAll('.node path[id]');

        simulation.alphaTarget(0.2).restart();

        rect.transition().duration(1000).ease(d3.easeElasticOut)
                .tween('circleResize', function(d) {
                    var src = d.r;
                    d.radius = scaleRadius(d.value);
                    var dst = (d.clicked || src == 0)? src : d.radius;
                    
                    let i = d3.interpolateNumber(src, dst);

                    return function(t) {

                        d.r = i(t);

                        if(gui_elements.scaled == false) simulation.force('collide', forceCollide);
                    }
                })
                .on('end', function(t) {
                    
                    simulation.alphaTarget(0);
                                       
                })
                .on('interrupt', function() {
                    
                    simulation.alphaTarget(0);
                });

        if(arcPath._groups[0].length > 0) {
            searchKeywords(data.searchedWords, true);
        }
    });

    searchInput = gui.add(gui_elements, 'search for words').onFinishChange(function(text) {
        text = text.toLowerCase();
        searchKeywords(text, false);             
    });

    searchInput.__input.placeholder = 'e.g. art+science+...';

    gui.add(gui_elements, 'clear search');
}