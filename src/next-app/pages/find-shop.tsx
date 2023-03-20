import type { NextPage } from 'next';
import { ChangeEvent, useState } from 'react';
import Button from '../components/Button';
import DropdownField from '../components/DropdownField';
import Header from '../components/Header';
import TextField from '../components/TextField';
import { serviceTypes } from '../constants/service-types';
import styles from '../styles/pages/FindShop.module.css';
import formStyles from '../styles/pages/Form.module.css';
import { useRouter } from 'next/router';
import Cookies from 'js-cookie';

const FindShopPage: NextPage = () => {
  const [postalCode, setPostalCode] = useState('');
  const [shopName, setShopName] = useState('');
  const [serviceType, setServiceType] = useState('');
  const [checked, setChecked] = useState(false);
  const valid = postalCode.length > 0;
  const router = useRouter();

  const handleCheckboxChange = (e: ChangeEvent<HTMLInputElement>) => {
    setChecked(e.target.checked);
  };

  const handleSubmit = () => {
    Cookies.set("pocode", postalCode);
    router.push({ pathname: '/shop-results' });
  };

  return (
    <div className={formStyles['page-container']}>
      <Header title="Find Shop" />

      <div className={formStyles.content}>
        <div className={formStyles['field-container']}>
          <TextField
            name="Your Location"
            placeholder="Enter your postal code"
            onChange={setPostalCode}
            required
          />
        </div>
        <div className={formStyles['field-container']}>
          <TextField name="Shop Name" placeholder="Search for a specific shop" />
        </div>
        <div className={formStyles['field-container']}>
          <DropdownField name="Service Type" items={serviceTypes} onSelect={setServiceType} />
        </div>
        <div className={formStyles['field-container']}>
          <input type="checkbox" checked={checked} onChange={handleCheckboxChange} />
          <label style={{ marginLeft: '1vw' }}>Show direct booking shops only</label>
        </div>
        <div className={formStyles['submit-container']}>
          <Button title="Search" disabled={!valid} width="80%" onClick={handleSubmit} />
        </div>
      </div>
    </div>
  );
};

export default FindShopPage;
