/**
 * Components to display the status of the cart in the navigation bar, and to navigate to cart
 * pages.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { DropdownMenu, DropdownMenuSep } from '../../libs/ui/dropdown-menu';
import { NavItem } from '../../libs/ui/navbar';
import { svgIcon } from '../../libs/svg-icons';
import { truncateString } from '../globals';
import { CartClearModal } from './clear';
import CartShare from './share';


/**
 * Renders the cart icon menu and count or in-progress spinner in the nav bar.
 */
const CartNavTitle = ({ elements, inProgress, locked }) => {
    let status;
    let iconClass = '';

    if (inProgress) {
        status = svgIcon('spinner');
        iconClass = 'cart__nav-spinner';
    } else if (elements.length > 0) {
        status = elements.length;
        iconClass = 'cart__nav-count';
    }
    return (
        <div className="cart__nav">
            <div className={`cart__nav-icon${status ? '' : ' cart__nav-icon--empty'}`}>
                {svgIcon('cart', { fill: locked ? '#e59545' : '#fff' })}
            </div>
            {status ? <div className={iconClass}>{status}</div> : null}
        </div>
    );
};

CartNavTitle.propTypes = {
    /** Array of cart contents */
    elements: PropTypes.array.isRequired,
    /** True if global cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** True if cart is locked */
    locked: PropTypes.bool.isRequired,
};


/**
 * Navigation bar item for the cart menu.
 */
class CartStatusComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            /** True if Share Cart modal is visible */
            shareModalOpen: false,
            clearModalOpen: false,
        };
        this.shareCartClick = this.shareCartClick.bind(this);
        this.closeShareCart = this.closeShareCart.bind(this);
        this.clearCartClick = this.clearCartClick.bind(this);
        this.closeClearCart = this.closeClearCart.bind(this);
    }

    /**
     * Called when the Share Cart menu item is clicked.
     */
    shareCartClick() {
        this.setState({ shareModalOpen: true });
    }

    /**
     * Called when the Share Cart modal close buttons are clicked.
     */
    closeShareCart() {
        this.setState({ shareModalOpen: false });
    }

    /**
     * Called when the Share Cart menu item is clicked.
     */
    clearCartClick() {
        this.setState({ clearModalOpen: true });
    }

    /**
     * Called when the Share Cart modal close buttons are clicked.
     */
    closeClearCart() {
        this.setState({ clearModalOpen: false });
    }

    render() {
        const { elements, savedCartObj, inProgress, openDropdown, dropdownClick, loggedIn } = this.props;
        const locked = !!(savedCartObj && savedCartObj.locked);

        if (loggedIn || elements.length > 0 || inProgress) {
            // Define the menu items for the Cart Status menu.
            const cartName = (loggedIn && savedCartObj && savedCartObj.name) ? truncateString(savedCartObj.name, 22) : '';
            const menuItems = [];
            const viewCartItem = <a key="view" href="/cohort-view/">View cohort</a>;
            const clearCartItem = <button key="clear" onClick={this.clearCartClick}>Clear cohort</button>;
            const lockIcon = cartName ? <div className="cart-nav-lock">{svgIcon(locked ? 'lockClosed' : 'lockOpen')}</div> : null;
            if (loggedIn) {
                // The href is just to quiet ESLint for the bad href. This code shouldn't do this
                // but the CSS looks difficult to fix after the tooltip updates.
                menuItems.push(
                    <span key="name" className="disabled-menu-item">
                        {`Current: ${cartName}`}{lockIcon}
                    </span>,
                    <DropdownMenuSep key="sep-1" />
                );
                if (elements.length > 0) {
                    menuItems.push(
                        viewCartItem,
                        <button key="share" onClick={this.shareCartClick}>Share cohort</button>,
                        clearCartItem,
                        <DropdownMenuSep key="sep-2" />
                    );
                }
                menuItems.push(<a key="manage" href="/cohort-manager/">Cohort manager</a>);
            } else {
                menuItems.push(viewCartItem, clearCartItem);
            }

            return (
                <NavItem
                    dropdownId="cart-control"
                    dropdownTitle={<CartNavTitle elements={elements} locked={locked} inProgress={inProgress} />}
                    openDropdown={openDropdown}
                    dropdownClick={dropdownClick}
                    label={`${locked ? 'locked' : ''} cohort containing ${elements.length} ${elements.length > 1 ? 'items' : 'item'}`}
                    buttonCss="cart__nav-button"
                >
                    <DropdownMenu label="cart-control">
                        {menuItems}
                    </DropdownMenu>
                    {this.state.shareModalOpen ? <CartShare userCart={savedCartObj} closeShareCart={this.closeShareCart} /> : null}
                    {this.state.clearModalOpen ? <CartClearModal closeClickHandler={this.closeClearCart} /> : null}
                </NavItem>
            );
        }
        return null;
    }
}

CartStatusComponent.propTypes = {
    /** Cart contents as array of @ids */
    elements: PropTypes.array,
    /** Cached saved cart object */
    savedCartObj: PropTypes.object,
    /** True if global cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** ID of nav dropdown currently visible */
    openDropdown: PropTypes.string,
    /** Function to call when dropdown clicked */
    dropdownClick: PropTypes.func,
    /** True if user has logged in */
    loggedIn: PropTypes.bool,
};

CartStatusComponent.defaultProps = {
    elements: [],
    savedCartObj: null,
    openDropdown: '',
    dropdownClick: null,
    loggedIn: false,
};


const mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj || null,
    inProgress: state.inProgress,
    openDropdown: ownProps.openDropdown,
    dropdownClick: ownProps.dropdownClick,
    loggedIn: !!(ownProps.session && ownProps.session['auth.userid']),
});

const CartStatusInternal = connect(mapStateToProps)(CartStatusComponent);


/**
 * Public Redux component to display the cart menu in the navigation bar. This is a <Navbar> child
 * so it gets its properties automatically imported from <Navbar>.
 */
const CartStatus = ({ openDropdown, dropdownClick }, reactContext) => (
    <CartStatusInternal
        openDropdown={openDropdown}
        dropdownClick={dropdownClick}
        session={reactContext.session}
    />
);

CartStatus.propTypes = {
    /** ID of nav dropdown currently visible; copied from <Navbar> props */
    openDropdown: PropTypes.string,
    /** Function to call when dropdown clicked; copied from <Navbar> props */
    /** Note: Required, but props from React.cloneElement fail isRequired validation */
    dropdownClick: PropTypes.func,
};

CartStatus.defaultProps = {
    openDropdown: '',
    dropdownClick: null,
};

CartStatus.contextTypes = {
    session: PropTypes.object,
};

export default CartStatus;
