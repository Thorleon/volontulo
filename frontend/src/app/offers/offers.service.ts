import { Injectable } from '@angular/core';
import { Headers, Http, Response, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';

@Injectable()
export class OffersService {
  private url = 'http://localhost:8000/api/offers/';

  constructor (
    private http: Http
  ) {}

  getOffers() {
    let headers: Headers = new Headers({
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    });
    let options: RequestOptions = new RequestOptions({ headers: headers });

    return this.http.get(this.url, options)
      .map((res:Response) => res.json())
      .catch(this.handleError);
  }

  handleError(reject: Response | any) {
    const body = reject.json() || '';
    const err = body.error || JSON.stringify(body);
    return Observable.throw(err);
  }
}
