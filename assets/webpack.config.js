const path = require('path');
const webpack = require('webpack');
//const Chunks2JsonPlugin = require('chunks-2-json-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const AssetsPlugin = require('assets-webpack-plugin');

module.exports = (env, argv) => {
    const isDevelopment = argv.mode !== 'production';

    return {
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
        /*    watchOptions: {
                poll: true,
                ignored: /node_modules/
            },*/
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
                jQuery: 'jquery',
                moment: 'moment'
            }),
            new webpack.ContextReplacementPlugin(/moment[\/\\]locale$/, /de|en/),
            new MiniCssExtractPlugin({
                filename: '../css/webapp.[contenthash].css',
                chunkFilename: '[id].[hash].css'
            }),
            new CleanWebpackPlugin(),
            new AssetsPlugin({path: path.join(__dirname, '..', "static")})
        ]
    }
};