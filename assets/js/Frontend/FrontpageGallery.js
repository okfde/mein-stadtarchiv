import React from "react";
import { buildImageUrl } from '../Helper';
import ReactCardFlip from 'react-card-flip';

const { Component } = React;

export default class FrontpageGallery extends Component {
    state = {
        imageIds: [],
        imageIdsAlt: [],
        isFlipped: []
    };

    constructor() {
        super();
        this.state.documents = frontpageImages;

        for (let i = 0; i < 4; i++) {
            this.state.imageIds.push((i === 2) ? -1 : i);
            this.state.imageIdsAlt.push(4 + i);
            this.state.isFlipped.push(false);
            setTimeout(this.flipCard.bind(this, i), this.getRandomTime());
        }
    }

    render() {
        let boxes = [];
        for (let i = 0; i < 4; i++) {
            boxes.push(
                <div className="col-md-3" key={`flip-box-${i}`}>
                    <ReactCardFlip isFlipped={this.state.isFlipped[i]} flipDirection="horizontal">
                        {this.selectFlipBox(i, false)}
                        {this.selectFlipBox(i, true)}
                    </ReactCardFlip>
                </div>
            );
        }
        return (
            <div className="container-fluid no-gutters">
                <div className="row">
                    {boxes}
                </div>
            </div>
        );
    }

    selectFlipBox(id, alt) {
        if (this.state[(alt) ? 'imageIdsAlt' : 'imageIds'][id] >= 0) {
            return this.getFlipBox(this.state.documents[this.state[(alt) ? 'imageIdsAlt' : 'imageIds'][id]])
        }
        return this.getSpecialFlipBox(this.state[(alt) ? 'imageIdsAlt' : 'imageIds'][id]);
    }

    getFlipBox(document) {
        return(
            <div className="image-flip-box">
                <a href={`/document/${document.id}`}>
                    <img src={buildImageUrl(document.id, document.files[0].id, 300)} style={{width: '100%'}}/>
                </a>
            </div>
        );
    }

    getSpecialFlipBox(id) {
        if (id === -1) {
            return (
                <div className="image-flip-box-special">
                    <h4>Archive erforschen</h4>
                    <p>Lernen Sie Ihre eigene Stadt besser kennen!</p>
                </div>
            )
        }
        if (id === -2) {
            return (
                <div className="image-flip-box-special">
                    <h4>Archive erforschen</h4>
                    <p>Lernen Sie Ihre eigene Stadt besser kennen!</p>
                </div>
            )
        }
        if (id === -3) {
            return (
                <div className="image-flip-box-special">
                    <h4>Archive erforschen</h4>
                    <p>Lernen Sie Ihre eigene Stadt besser kennen!</p>
                </div>
            )
        }
        if (id === -4) {
            return (
                <div className="image-flip-box-special">
                    <h4>Archive erforschen</h4>
                    <p>Lernen Sie Ihre eigene Stadt besser kennen!</p>
                </div>
            )
        }
    }

    flipCard(id) {
        this.state.isFlipped[id] = !this.state.isFlipped[id];
        this.setState({
            isFlipped: this.state.isFlipped
        });
        setTimeout(this.changeImage.bind(this, id), 500);
    }

    changeImage(id) {
        if ([...this.state.imageIds, ...this.state.imageIdsAlt].filter(item => item < 0).length) {
            this.state[(this.state.isFlipped[id]) ? 'imageIds' : 'imageIdsAlt'][id] = this.getRandomImageId();
        }
        else {
            this.state[(this.state.isFlipped[id]) ? 'imageIds' : 'imageIdsAlt'][id] = this.getRandomSpecialImageId();
        }
        this.setState({
            [(this.state.isFlipped[id]) ? 'imageIds' : 'imageIdsAlt']: this.state[(this.state.isFlipped[id]) ? 'imageIds' : 'imageIdsAlt']
        });
        setTimeout(this.flipCard.bind(this, id), this.getRandomTime());
    }

    getRandomTime() {
        return 3000 + Math.random() * 6000;
    }

    getRandomImageId() {
        return Math.floor(Math.random() * this.state.documents.length);
    }

    getRandomSpecialImageId() {
        return (-1 * Math.floor(Math.random() * 4)) - 1;
    }
}