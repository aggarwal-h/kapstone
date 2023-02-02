import React, { useEffect, useState, useContext } from 'react';
import styles from '../styles/components/Navbar.module.css';
import Button from './Button';
import ProfileModal from './ProfileModal';
import { IoMdMenu, IoMdContact } from 'react-icons/io';
import Link from 'next/link';
import { CustomerNavbarData, ShopOwnerNavbarData } from '../constants/NavbarData';
import { IconContext } from 'react-icons';
import Cookies from 'js-cookie';
import { AuthContext, accountTypes, Jwt } from '../utils/api';
import { useRouter } from 'next/router';

type NavbarProps = {
  authData: Jwt;
  onLogin: (jwt: Jwt) => void;
}

const Navbar = (props: any) => {
  const router = useRouter();
  // const [authData, setAuthData] = useState(useContext(AuthContext));
  const [NavbarData, setNavBarData] = useState(CustomerNavbarData);
  const [buttonText, setButtonText] = useState("Login");
  const [sidebar, setSidebar] = useState(false);
  const [profile, setProfile] = useState(false);

  useEffect(() => {
    if (props.authData.access !== '') {
      setButtonText("Logout");
    } else if (Cookies.get('access') && Cookies.get('access') !== '') {
      setButtonText("Logout");
    }
    if (props.authData.user_type === 'shop_owner') {
      setNavBarData(ShopOwnerNavbarData);
    } else if (props.authData.user_type === 'employee') {
      // Need to figure out Employee Navbar Data
      // setNavBarData(EmployeeNavbarData)
    } else {
      setNavBarData(CustomerNavbarData);
    }
  }, [props.authData])

  const toggleSidebar = () => setSidebar((prevSidebar) => !prevSidebar);
  const toggleProfile = () => setProfile((prevProfile) => !prevProfile);

  const logout = () => {
    props.onLogin({
      'access': '',
      'refresh': '',
      'user_type': 'customer',
    })
    if (buttonText === 'Login') {
      router.push('/login');
    }

    Cookies.remove('access');
    Cookies.remove('refresh');
    Cookies.remove('user_type');
    router.push('/');
  };

  return (
    <div>
      <IconContext.Provider value={{ color: '#000' }}>
        <div className={styles.navbar}>
          <div className={sidebar ? styles['menu-bars-active'] : styles['menu-bars']}>
            <IoMdMenu onClick={toggleSidebar} />
          </div>
          <div className={styles['btn-contianer']}>
            <IoMdContact className={styles['profile-btn']} onClick={toggleProfile} />
            {profile ? <ProfileModal authData={props.authData} setAuthData={props.setAuthData} onLogin={props.onLogin} /> : null}
            <div className={styles['logout-btn']}>
              <Button title={buttonText} width="120%" onClick={logout} />
            </div>
          </div>
        </div>

        <nav className={sidebar ? styles['nav-menu-active'] : styles['nav-menu']}>
          <ul className={styles['nav-menu-items']} onClick={toggleSidebar}>
            {NavbarData.map((item, index) => {
              return (
                <li key={index} className={styles['nav-text']}>
                  <Link href={item.path}>
                    <div>
                      {item.icon}
                      <span className={styles['nav-text-item']}>{item.title}</span>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </IconContext.Provider>
    </div>
  );
}

export default Navbar;
