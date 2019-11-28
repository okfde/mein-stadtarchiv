import Uppy from '@uppy/core'
import XHRUpload from '@uppy/xhr-upload'


import React from "react";
const { Component } = React;
import { DragDrop } from '@uppy/react';


export default class CategoryFileUpload extends Component {

    state = {
        files: [],
    }

    constructor() {
        super()
        this.uppy = Uppy({id: 'uppy', autoProceed: true})
        this.uppy.use(XHRUpload, {
            id: 'XHRUpload',
            endpoint: `/admin/archive/${window.currentArchiveId}/category/${window.currentCategoryId}/upload`,
            responseType: 'text',
            fieldName: 'file',
            getResponseError: (text,response) => {
                try {
                    return new Error(JSON.parse(text).error)
                } catch (e) {
                    return new Error('Error Response not valid JSON')
                }
            }
        })
        this.uppy.on('upload', () => this.setState({files: this.uppy.getFiles()}))
        this.uppy.on('upload-progress', () => this.setState({files: this.uppy.getFiles()}))
        this.uppy.on('upload-success', () => this.setState({files: this.uppy.getFiles()}))
        this.uppy.on('upload-error', () => this.setState({files: this.uppy.getFiles()}))

    }

    componentWillUnmount () {
        this.uppy.close()
    }

    componentDidMount() {

    }

    getFileStatus(file) {
        if (file.error) {
            return file.error
        }
        if (file.progress.precentage < 100 ) {
            return `Fortschritt: ${file.progress.precentage}`
        }
        return "Fertig"
    }

    render() {
        const rows = this.state.files.map((file) => {
            return <tr key={file.id}>
                <td>
                    {file.name}
                </td>
                <td>
                    { this.getFileStatus(file)}
                </td>
            </tr>
        })

        return <div>
            <DragDrop uppy={this.uppy}         locale={{
                strings: {
                    dropHereOr: 'Dateien hierherziehen oder %{browse}',
                    browse: 'auswählen'
                }
            }} />
            {!!rows.length && <table className='table mt-2'>
                <thead>
                <tr>
                    <th>Dateiname</th>
                    <th>Status</th>
                </tr>
                </thead>
                <tbody>
                {rows}
                </tbody>
            </table>}
        </div>
    }
}