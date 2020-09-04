from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum
from collections import UserList, UserDict

class PersonalCapitalList(UserList):
  def from_resp(self, dictionary={}, header={}, data=[], fetchResp={}):
    self.__dict__ = {**self.__dict__, **dictionary}
    self.spHeader = header
    self.data = data
    self.fetchResponse = fetchResp
    return self

class PersonalCapitalDict(UserDict):
  def from_resp(self, dictionary={}, header={}, data=[], fetchResp={}):
    self.__dict__ = {**self.__dict__, **dictionary}
    self.spHeader = header
    self.data = data
    self.fetchResponse = fetchResp
    return self

class PersonalCapitalExpress(PersonalCapital):
  """Wrapper class for Personal Capital API, which simplifies login flow and API calls"""
  def default_tf_callback(self):
    return input('2FA Code: ')

  def quick_login(self,
                  username, 
                  password, 
                  two_factor='sms', 
                  tf_callback=default_tf_callback):
    """A quicker login flow with less boilerplate code
    Arguments:
      username:     username
      password:     password
      two_factor:   a string specifying the method.  Options are 'none', 'sms', or 'email'
      tf_callback:  a function that will handle the 2FA confirmation.  This callback has no arguments and returns only the 2FA code.
    """
    try:
      self.login(username, password)
    except RequireTwoFactorException:
      self.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
      self.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, input('SMS Code: '))
      self.authenticate_password(password)
  #TODO: different flows for each 2FA method

  def _get_generic(self, endpoint, kw_args={}):
    """generic fetch and error handling for all API calls"""
    response = self.fetch(endpoint, kw_args)
    if not response.ok:
      raise response.raise_for_status()
    return response
  #TODO: throw exceptions on spHeader errors
  
  def getAccounts(self):
    resp = self._get_generic('/newaccount/getAccounts2')
    return PersonalCapitalList().from_resp(dictionary=resp.json()['spData'],
                                           header=resp.json()['spHeader'],
                                           data=resp.json()['spData']['accounts'],
                                           fetchResp=resp,
                                           )

  def getCategories(self):
    resp = self._get_generic('/transactioncategory/getCategories')
    return PersonalCapitalList().from_resp(header=resp.json()['spHeader'],
                                           data=resp.json()['spData'],
                                           fetchResp=resp,
                                           )
    
  def getPerson(self):
    resp = self._get_generic('/person/getPerson')
    return PersonalCapitalDict().from_resp(dictionary=resp.json()['spData'],
                                           header=resp.json()['spHeader'],
                                           data=resp.json()['spData'],
                                           fetchResp=resp,
                                           )

  def getUserMessages(self):
    resp = self._get_generic('/message/getUserMessages')
    return PersonalCapitalList().from_resp(dictionary=resp.json()['spData'],
                                           header=resp.json()['spHeader'],
                                           data=resp.json()['spData']['userMessages'],
                                           fetchResp=resp,
                                           )
  
  def _getHistories(self,
                    userAccountIds=None,
                    startDate=None,
                    endDate=None,
                    interval='DAY',
                    types='balances',
                    resp_list='histories',
                    **kwargs
                    ):
    """Gets all transactions for the specified criteria.  No attributes are
    required, but the known attributes are shown with defaults as 'None'.  This
    method will accept other parameters for others that are discovered.
      userAccountIds: array of user account numbers
                      must be a string of a list (with brackets in the string)
      startDate: Python datetime.date object for beginning of range
      endDate: Python datetime.date object for end of range
      types: must be a string of a list (with brackets in the string)

    Parameters the seem deprecated:
      sort_cols
      sort_rev
      start_page
      rows_per_page
      component
    """
    if userAccountIds is not None:
      kwargs['userAccountIds'] = userAccountIds
    if startDate is not None:
      kwargs['startDate'] = startDate.isoformat()
    if endDate is not None:
      kwargs['endDate'] = endDate.isoformat()
    if interval is not None:
      kwargs['interval'] = interval
    if types is not None:
      kwargs['types'] = '["' + types + '"]'

    resp = self._get_generic('/account/getHistories', kwargs)
    return PersonalCapitalList().from_resp(dictionary=resp.json()['spData'],
                                            header=resp.json()['spHeader'],
                                            data=resp.json()['spData'][resp_list],
                                            fetchResp=resp,
                                            )

  def getBalancesHistories(self,
                           userAccountIds=None,
                           startDate=None,
                           endDate=None,
                           interval='DAY',
                           **kwargs
                           ):
    return self._getHistories(
        userAccountIds=userAccountIds, startDate=startDate, endDate=endDate, 
        interval=interval, types='balances","dailyChangeAmount', resp_list='histories', **kwargs)

  def getNetWorthHistories(self,
                           userAccountIds=None,
                           startDate=None,
                           endDate=None,
                           interval='DAY',
                           **kwargs
                           ):
    return self._getHistories(
        userAccountIds=userAccountIds, startDate=startDate, endDate=endDate, 
        interval=interval, types='networth', resp_list='networthHistories', **kwargs)

  def getSummaryHistories(self,
                          userAccountIds=None,
                          startDate=None,
                          endDate=None,
                          interval='DAY',
                          **kwargs
                          ):
    return self._getHistories(
        userAccountIds=userAccountIds, startDate=startDate, endDate=endDate, 
        interval=interval, types='summaries', resp_list='accountSummaries', **kwargs)


  def getUserTransactions(self,
                          userAccountIds=None,
                          startDate=None,
                          endDate=None,
                          **kwargs
                          ):
    """Gets all transactions for the specified criteria.  No attributes are
    required, but the known attributes are shown with defaults as 'None'.  This
    method will accept other parameters for others that are discovered.
      userAccountIds: array of user account numbers
                     must be a string of a list (with brackets in the string)
      startDate: Python datetime.date object for beginning of range
      endDate: Python datetime.date object for end of range

    Parameters the seem deprecated:
      sort_cols
      sort_rev
      start_page
      rows_per_page
      component
    """
    if userAccountIds is not None:
      kwargs['userAccountIds'] = userAccountIds
    if startDate is not None:
      kwargs['startDate'] = startDate.isoformat()
    if endDate is not None:
      kwargs['endDate'] = endDate.isoformat()

    resp = self._get_generic('/transaction/getUserTransactions', kwargs)
    return PersonalCapitalList().from_resp(dictionary=resp.json()['spData'],
                                           header=resp.json()['spHeader'],
                                           data=resp.json()['spData']['transactions'],
                                           fetchResp=resp,
                                           )
