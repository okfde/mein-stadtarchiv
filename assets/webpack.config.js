const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const AssetsPlugin = require('assets-webpack-plugin');
const MomentTimezoneDataPlugin = require('moment-timezone-data-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = (env, argv) => {
    const isDevelopment = argv.mode !== 'production';

    let result = {
        entry: [
            `./assets/js/base.js`,
            `./assets/js/webapp.js`
        ],
        resolve: {
            alias: {
                jquery: "jquery/src/jquery",
                $: "jquery/src/jquery",
                'mapbox-gl': 'mapbox-gl/dist/mapbox-gl',
            }
        },
        mode: isDevelopment ? 'development' : argv.mode,
        output: {
            path: path.join(__dirname, '..', 'static', 'js'),
            publicPath: '/static/js',
            filename: 'webapp.[contenthash].' + ((isDevelopment) ? '' : 'min.') + 'js',
        },
        optimization: {
            minimize: !isDevelopment
        },
        performance: {
            hints: false
        },
        module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /node_modules\/((?!bootstrap).)+/,
                    loader: 'babel-loader',
                    query: {
                        presets: ['@babel/preset-env', '@babel/preset-react']
                    }
                },
                {
                    test: /\.module\.s(a|c)ss$/,
                    loader: [
                        isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
                        {
                            loader: 'css-loader',
                            options: {
                                modules: true,
                                sourceMap: isDevelopment
                            }
                        },
                        {
                            loader: 'sass-loader',
                            options: {
                                sourceMap: isDevelopment
                            }
                        }
                    ]
                },
                {
                    test: /\.s(a|c)ss$/,
                    exclude: /\.module.(s(a|c)ss)$/,
                    loader: [
                        isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
                        'css-loader',
                        {
                            loader: 'sass-loader',
                            options: {
                                sourceMap: isDevelopment
                            }
                        }
                    ]
                }
            ]
        },
        devtool: isDevelopment ? "eval-source-map" : "source-map",
        plugins: [
            new webpack.ProvidePlugin({
                $: 'jquery',
                jQuery: 'jquery'
            }),
            new MomentTimezoneDataPlugin({
                matchZones: ["Europe/Berlin", 'Etc/UTC'],
                startYear: 1400,
                endYear: 2030,
            }),
            new MiniCssExtractPlugin({
                filename: '../css/webapp.[contenthash].css',
                chunkFilename: '[id].[hash].css'
            }),
            new CleanWebpackPlugin(),
            new AssetsPlugin({path: path.join(__dirname, '..', "static"), filename: 'webpack-assets.' + ((isDevelopment) ? '' : 'min.') + 'json'})
        ]
    };

    if (isDevelopment) {
        result.plugins.push(
            new BundleAnalyzerPlugin({
                analyzerHost: '0.0.0.0'
            })
        );
    }
    return result;
};