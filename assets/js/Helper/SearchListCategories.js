import React from "react";

const { Component } = React;

export default class SearchListCategories extends Component {
    state = {
        initialized: false,
        categorySelectorOpen: false,
        status: 'ready',
        current: {
            id: 'all',
            title: 'Alle Archive'
        },
        parent: null,
        children: archives,
        csrf_token: csrf_token
    };

    apiUrl = '/api/search/category';

    toggleCategorySelectorOpen() {
        this.setState({
            categorySelectorOpen: !this.state.categorySelectorOpen
        });
    }

    constructor(props) {
        super(props);
        this.onUpdate = props.onUpdate;
    }

    selectCategory(category) {
        this.onUpdate(category.id);
        this.setState({
            status: 'loading',
            current: category
        });
        this.getCategoryData(category.id);
    }

    getCategoryData(category) {
        $.post(this.apiUrl, {csrf_token: csrf_token, category: category})
            .then((data) => {
                this.setState({
                    status: 'ready',
                    parent: data.parent,
                    children: data.children
                });
            });
    }

    render() {
        let options = [];
        if (this.state.parent) {
            options.push(this.renderCategory(this.state.parent, 'parent'))
        }
        else {
            options.push(this.renderCategory({id: 'root', title: 'Eine Ebene hoch'}, 'parent', true))
        }
        for (let i = 0; i < this.state.children.length; i++) {
            options.push(this.renderCategory(this.state.children[i], 'child'));
        }
        return (
            <div id="category-field">
                <p id="category-current" onClick={this.toggleCategorySelectorOpen.bind(this)}>
                    {this.state.current.title}
                </p>
                {this.state.categorySelectorOpen && this.state.status === 'loading' &&
                    <div id="category-search" className="category-search-loading">
                        <i className="fa fa-spinner fa-pulse fa-fw"></i>
                    </div>
                }
                {this.state.categorySelectorOpen && this.state.status === 'ready' &&
                    <ul id="category-search">
                        {options}
                    </ul>
                }
            </div>
        );
    }

    renderCategory(category, type, disabled) {
        return (
            <li
                data-uid={category.id} className={`category-${type} ${(disabled) ? 'disabled' : ''}`}
                key={category.id}
                onClick={this.selectCategory.bind(this, category)}
            >
                {type === 'parent' &&
                    <i className="fa fa-arrow-circle-o-left" aria-hidden="true"></i>
                }
                {type === 'child' &&
                    <i className="fa fa-arrow-circle-o-right" aria-hidden="true"></i>
                }
                {' '}{category.title}
            </li>
        );
    }

}