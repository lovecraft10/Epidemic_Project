var ec_right2 = echarts.init(document.getElementById('r2'), "dark");

var ec_right2_option = {
                        // backgroundColor: '#515151',
						title : {
						    text : "今日疫情热搜",
						    textStyle : {
						        color : 'white',
						    },
						    left : 'left'
						},
                        tooltip: {
                            show: false
                        },
                        series: [{
                                type: 'wordCloud',
								// drawOutOfBound:true,
                                gridSize: 1,
                                sizeRange: [12, 55],
                                rotationRange: [-45, 0, 45, 90],
                                // maskImage: maskImage,

                                //这是让词云图的颜色随机
                                textStyle: {
                                    normal: {
                                        color: function () {
                                            return 'rgb(' +
                                                    Math.round(Math.random() * 255) +
                                                    ', ' + Math.round(Math.random() * 255) +
                                                    ', ' + Math.round(Math.random() * 255) + ')'
                                        }
                                    }
                                },
                                // left: 'center',
                                // top: 'center',
                                // // width: '96%',
                                // // height: '100%',
                                right: null,
                                bottom: null,
                                // width: 300,
                                // height: 200,
                                // top: 20,
                                data:  []
                            }]
                    }
