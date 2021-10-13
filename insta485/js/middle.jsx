import React from 'react';
import PropTypes, { string } from 'prop-types';
import moment from 'moment';
import Post from './post';


class Batch extends React.Component {
    constructor(props) {
      super(props);
      this.state = {links: [], sub:''};
    }

    pass = () => {
        return '';
    }
    
    componentDidMount() {
        const{ url } = this.props;
        fetch(url, {credentials: 'same-origin', method: 'GET'})
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
        })
        .then((data) => {
            this.setState({
                links: data.results,
                sub:''
            });
        })
        .catch((error) => console.log(error));
    }

    render () {
        const {links, sub} = this.state;
        return (
            <section className="feed">
                {links.map((post) => (
                <div className="">
                    <Post url={post.url}/>
                </div>))}
            </section>
        );
    }
}

Batch.propTypes = {
    url: PropTypes.string.isRequired,
};

export default Batch;